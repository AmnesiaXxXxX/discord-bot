import discord
from discord import app_commands
from discord.ext import commands
from config import Config


class CustomCommandTree(app_commands.CommandTree):
    async def on_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        message = f"Произошла ошибка: {error}"
        if Config.DEBUG:
            message += f"\n```{error.__traceback__}```"
        await interaction.response.send_message(message, ephemeral=True)
