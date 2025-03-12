import logging
import discord
from discord.ext import commands
from utils.database import Database
from config import Config
from globals import yes
from utils.menu_state import MenuManager, MenuState
from help_command import HelpCommand
import asyncio
import aiohttp
import os
import re
from typing import Sequence
import atexit
from loggers import setup_discord_loggers, compress_latest_log

atexit.register(compress_latest_log)

setup_discord_loggers()
config = Config()
menu_manager = MenuManager()

logger = logging.getLogger("discord")
intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(
    command_prefix=Config.PREFIX,
    intents=intents,
    help_command=HelpCommand(),
)

db = Database()


def find_urls(text):
    return re.findall(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        text,
    )


async def download_file(url: str, save_path: str) -> discord.File:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    file_content = await response.read()

                    # Разбиваем URL на имя файла
                    file_name = url.split("/")[-1].split("?")[0]
                    # Создаем полный путь к файлу, если он не указан
                    if not os.path.isabs(save_path):
                        save_path = os.path.join(os.getcwd(), save_path)

                    # Добавляем имя файла к пути
                    full_save_path = os.path.join(save_path, file_name)

                    # Сохраняем файл локально
                    with open(full_save_path, "wb") as f:
                        f.write(file_content)

                    return discord.File(full_save_path)
                else:
                    raise Exception(
                        f"Не удалось скачать файл. Код ошибки: {response.status}"
                    )
    except Exception as e:
        raise Exception(f"Произошла ошибка при скачивании файла: {e}")


@bot.event
async def on_ready():
    logger.info("Старт!")
    db.create_tables()


@bot.event
async def on_command_error(ctx: commands.Context, error: Exception):
    message = "`Error`"
    logger.error(f"Ошибка при выполнении команды: {error}", exc_info=True)
    match type(error):
        case commands.CommandInvokeError:
            message = "Произошла ошибка"

        case commands.MissingPermissions:
            message = "У вас недостаточно прав на исполнение команды"
        case commands.CommandNotFound:
            return
        case _:
            message = "Произошла ошибка"
    if Config.DEBUG:

        message += f"\n```{error}```"
    if isinstance(message, str):
        await ctx.send(message, ephemeral=True)


class MenuCommands(commands.Cog):
    """Команды для взаимодействия с меню для создания постов"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def create_post(self, ctx: commands.Context):
        """Начать создания поста"""
        menu_manager.start_menu(ctx.author.id, ctx.channel.id)
        msg = await ctx.reply("Введите текст:", silent=True, ephemeral=True)
        menu_manager.add_message_to_delete(ctx.author.id, msg)
        menu_manager.add_message_to_delete(ctx.author.id, ctx.message)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def add_role_to_ping(self, ctx: commands.Context, _roles: str):
        """Добавить роли для упоминания ботом, можно несколько через запятую без пробелов"""
        logger.info(_roles)
        chat_id = ctx.message.guild.id if ctx.message.guild else 123
        roles_to_remove = list(
            set([role for role in _roles.split(",") if role.startswith("<@")])
        )
        db.set_rolenames(
            chat_id,
            roles_to_remove,
        )
        await self.list_role_to_ping(ctx)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def remove_role_to_ping(self, ctx: commands.Context, _roles: str):
        """Убрать роли для упоминания ботом, можно несколько через запятую без пробелов"""
        chat_id = ctx.message.guild.id if ctx.message.guild else 123

        # Получаем список ролей, которые нужно удалить
        roles_to_remove = list(
            set([role for role in _roles.split(",") if role.startswith("<@")])
        )
        logger.info(roles_to_remove)
        # Если есть роли для удаления, обновляем запись в базе
        if roles_to_remove:
            # Обновляем rolenames в базе
            db.set_rolenames(chat_id, ",".join(roles_to_remove))

        # Отправляем обновленный список
        await self.list_role_to_ping(ctx)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def list_role_to_ping(self, ctx: commands.Context):
        """Список ролей которые будет упоминать бот"""
        chat_id = ctx.message.guild.id if ctx.message.guild else 123
        await ctx.message.reply(
            ", ".join(db.get_rolenames(chat_id))
            or "Добавьте роли через !add_role_to_ping"
        )

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def complete(self, ctx: commands.Context):
        """Вывод сообщения об успешном завершении задания. Для пометки конкретного задания ответить на сообщение"""
        await ctx.message.delete()
        reference = ctx.message.reference.resolved if ctx.message.reference else None
        if isinstance(reference, discord.Message):
            embeds = reference.embeds if reference.embeds else None
            if not embeds:
                raise ValueError("У этого сообщения нет embeds")
            embeds.append(menu_manager.get_task_complete_embed())
            await reference.edit(embeds=embeds)

        else:
            await ctx.message.channel.send(embed=menu_manager.get_task_complete_embed())


class UtilityCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @commands.command()
    # @commands.has_permissions(administrator=True)
    async def repeat_me(self, ctx: commands.Context, args):
        """Команда для проверки аргументов"""
        await ctx.message.reply(args)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ping(self, ctx: commands.Context):
        """Команда для проверки работоспособности"""
        await ctx.message.add_reaction(yes)


class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def debug(self, ctx: commands.Context, level: bool):
        """
        Изменить уровень отладки
        Использование: !debug True/False
        """
        try:
            Config().update_debug_level(level)
            await ctx.message.add_reaction(yes)
            await ctx.send(
                f"Уровень отладки изменен на: {'DEBUG' if level else 'INFO'}",
                ephemeral=True,
            )
        except Exception as e:
            await ctx.send(f"Ошибка при изменении уровня отладки: {str(e)}")


# @bot.command()
async def multi_image(ctx: commands.Context):
    image_urls = [
        "https://efspb.ru/upload/iblock/209/ig78ehdky1d5p28ujt7nyund94ex797x.jpg",
        "https://www.meatprod.ru/upload/e85a11867d490a6f7c122f24eeedc79a.jpg",
        "https://f-o-o-d.ru/upload/iblock/635/5gc0rdkq3r33zdvhwfkcze83t8f3d706/kurinniye_yaza_polza_i_vred.jpg",
    ]
    embeds = []
    for url in image_urls:
        embed = discord.Embed(url="https://amnesiawho.ru/")
        embed.set_image(url=url)
        embeds.append(embed)
    await ctx.send(embeds=embeds)


# @bot.command()
async def download(ctx: commands.Context, url: str):
    await ctx.message.reply("Файл скачан", file=await download_file(url, "temp/"))


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    if message.content.startswith(Config.PREFIX):
        await bot.process_commands(message)
        return

    user_id = message.author.id
    current_state = menu_manager.get_current_state(user_id)

    if not current_state:
        return

    if not menu_manager.check_channel(user_id, message.channel.id):
        return

    menu_manager.add_message_to_delete(user_id, message)
    logger.info(current_state)
    if current_state in list(MenuState):
        if current_state == MenuState.EMBED_PHOTO:
            if len(message.attachments) > 0:
                menu_manager.user_data[user_id]["EMBED_PHOTO"] = [
                    img.url for img in message.attachments
                ]

                next_state, prompt = menu_manager._get_next_state_and_prompt(
                    current_state
                )

                menu_manager.user_states[user_id] = next_state
                if prompt:
                    reply = await message.reply(prompt, silent=True)
                    menu_manager.add_message_to_delete(user_id, reply)

                    menu_manager.add_message_to_delete(user_id, reply)
            if message.content.lower() == "нет":
                next_state, prompt = menu_manager._get_next_state_and_prompt(
                    current_state
                )
                menu_manager.user_states[user_id] = next_state
                await message.reply(prompt)
        elif current_state == MenuState.EMBED_FILES:
            if find_urls(message.content):
                menu_manager.user_data[user_id]["EMBED_FILES"] = [
                    await download_file(url, "temp/")
                    for url in find_urls(message.content)
                ]
                menu_manager.user_states[user_id] = MenuState.FINISHED

            if message.content.lower() == "нет":
                next_state, prompt = menu_manager._get_next_state_and_prompt(
                    current_state
                )
                menu_manager.user_states[user_id] = next_state

        else:
            response = menu_manager.process_answer(user_id, message.content)
            if response:
                reply = await message.reply(response, silent=True)
                menu_manager.add_message_to_delete(user_id, reply)
        if menu_manager.user_states[user_id] == MenuState.FINISHED:
            del menu_manager.user_states[user_id]
            roles_to_ping = ", ".join(db.get_rolenames(message.channel.id)) or None
            summary_embed = menu_manager.get_summary_embed(user_id)
            msg = await message.channel.send(
                content=roles_to_ping,
                embeds=summary_embed,
            )
            files = menu_manager.user_data[user_id]["EMBED_FILES"]

            if (
                isinstance(files, str)
                and isinstance(files, list)
                and not (
                    isinstance(files, Sequence)
                    and all(isinstance(f, discord.File) for f in files)
                )
            ):
                await menu_manager.delete_user_messages(user_id)
            thread = await msg.create_thread(name="Файлы")
            await thread.send(files=files)  # type: ignore
            await menu_manager.delete_user_messages(user_id)


def add_cog_sync(bot: commands.Bot, commands: commands.Cog):
    asyncio.run(bot.add_cog(commands))


if __name__ == "__main__":
    add_cog_sync(bot, MenuCommands(bot))
    add_cog_sync(bot, UtilityCommands(bot))
    add_cog_sync(bot, AdminCommands(bot))
    bot.run(Config.DISCORD_TOKEN)
