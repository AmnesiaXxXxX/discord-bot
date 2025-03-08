import logging
import discord
from discord.ext import commands
from utils.database import Database
from config import Config
from tree_cls import CustomCommandTree
from globals import yes, no
from utils.menu_state import MenuManager, MenuState
from help_command import HelpCommand
import asyncio

config = Config()
menu_manager = MenuManager()

logger = logging.getLogger("discord")
intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(
    command_prefix=Config.PREFIX,
    intents=intents,
    tree_cls=CustomCommandTree,
    help_command=HelpCommand(),
)

db = Database()


@bot.event
async def on_ready():
    logger.info("Старт!")


@bot.event
async def on_command_error(ctx: commands.Context, error):
    match type(error):
        case commands.CommandInvokeError:
            message = "Произошла ошибка"
            if Config.DEBUG:
                message += f"\n```{error}```"

        case commands.MissingPermissions:
            message = "У вас недостаточно прав на исполнение команды"
        case _:
            message = "Произошла ошибка"
    await ctx.reply(message, ephemeral=True)


class MenuCommands(commands.Cog):
    """Команды для взаимодействия с меню для создания постов"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def start_menu(self, ctx: commands.Context):
        """Начать создания поста"""
        menu_manager.start_menu(ctx.author.id, ctx.channel.id)
        msg = await ctx.reply("Введите текст:", silent=True, ephemeral=True)
        menu_manager.add_message_to_delete(ctx.author.id, msg)
        menu_manager.add_message_to_delete(ctx.author.id, ctx.message)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def complete(self, ctx: commands.Context):
        """Вывод сообщения об успешном завершении задания"""
        await ctx.message.delete()
        await ctx.message.channel.send(embed=menu_manager.get_task_complete_embed())


class UtilityCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
            if message.attachments:
                menu_manager.user_data[user_id]["EMBED_PHOTO"] = message.attachments[
                    0
                ].url
                menu_manager.user_states[user_id] = MenuState.FINISHED
                summary_embed = menu_manager.get_summary_embed(user_id)
                await message.channel.send(embed=summary_embed)
                await menu_manager.delete_user_messages(user_id)
            elif message.content.lower() == "нет":
                menu_manager.user_states[user_id] = MenuState.FINISHED
                summary_embed = menu_manager.get_summary_embed(user_id)
                await message.channel.send(embed=summary_embed)
                await menu_manager.delete_user_messages(user_id)
        else:
            response = menu_manager.process_answer(user_id, message.content)
            if response:
                reply = await message.reply(response, silent=True)
                menu_manager.add_message_to_delete(user_id, reply)


def add_cog_sync(bot: commands.Bot, commands: commands.Cog):
    asyncio.run(bot.add_cog(commands))


if __name__ == "__main__":
    add_cog_sync(bot, MenuCommands(bot))
    add_cog_sync(bot, UtilityCommands(bot))
    add_cog_sync(bot, AdminCommands(bot))
    bot.run(Config.DISCORD_TOKEN)
