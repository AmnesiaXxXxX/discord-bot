from typing import List, Mapping, Optional

import discord
from discord.ext import commands


class HelpCommand(commands.HelpCommand):
    async def send_bot_help(
        self, mapping: Mapping[Optional[commands.Cog], List[commands.Command]]
    ) -> None:
        embed: discord.Embed = discord.Embed(
            title="Команды бота", color=discord.Color.blue()
        )
        for cog, commands_list in mapping.items():
            if not commands_list:
                continue
            commands_desc = []
            for cmd in commands_list:
                desc = f"{cmd.name}"
                if cmd.help:
                    desc += f" - {cmd.help}"
                commands_desc.append(desc)
            text = "\n\n".join(commands_desc)
            embed.add_field(
                name=(
                    f"{cog.qualified_name} {('- ' + cog.description) if cog.description else ''}"
                    if cog
                    else "Без категории"
                ),
                value=f"```{str(text)}```",
                inline=False,
            )
        channel: discord.abc.Messageable = self.get_destination()
        await channel.send(embed=embed)

    async def send_command_help(self, command: commands.Command) -> None:
        embed: discord.Embed = discord.Embed(
            title=command.name,
            description=command.help or "Описание отсутствует",
            color=discord.Color.blue(),
        )
        channel: discord.abc.Messageable = self.get_destination()
        await channel.send(embed=embed)

    async def send_cog_help(self, cog: commands.Cog) -> None:
        embed: discord.Embed = discord.Embed(
            title=cog.qualified_name,
            description=cog.description or "Описание отсутствует",
            color=discord.Color.blue(),
        )
        for command in cog.get_commands():
            help_text = command.help or "Описание отсутствует"
            if command.brief:
                help_text = f"{command.brief}\n{help_text}"
            embed.add_field(
                name=command.name,
                value=help_text,
                inline=False,
            )
        channel: discord.abc.Messageable = self.get_destination()
        await channel.send(embed=embed)

    async def send_group_help(self, group: commands.Group) -> None:
        embed: discord.Embed = discord.Embed(
            title=group.name,
            description=group.help or "Описание отсутствует",
            color=discord.Color.blue(),
        )
        for command in group.commands:
            help_text = command.help or "Описание отсутствует"
            if command.brief:
                help_text = f"{command.brief}\n{help_text}"
            embed.add_field(
                name=command.name,
                value=help_text,
                inline=False,
            )
        channel: discord.abc.Messageable = self.get_destination()
        await channel.send(embed=embed)
