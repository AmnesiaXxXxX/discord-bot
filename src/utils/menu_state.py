import discord
from enum import Enum
from typing import Dict, Optional, Tuple
import asyncio

class MenuState(Enum):
    """Перечисление возможных состояний меню."""

    EMBED_TEXT = 1
    EMBED_CONTENT = 2
    EMBED_PHOTO = 3
    FINISHED = 4


class MenuManager:
    """Менеджер для управления состояниями меню и данными пользователей."""

    __slots__ = ("user_states", "user_data", "messages_to_delete", "user_channels")

    def __init__(self) -> None:
        """Инициализация MenuManager с пустыми словарями состояний и данных."""
        self.user_states: Dict[int, MenuState] = {}
        self.user_data: Dict[int, Dict[str, str]] = {}
        self.messages_to_delete: Dict[int, list[discord.Message]] = {}
        self.user_channels: Dict[int, int] = {}

    def get_current_state(self, user_id: int) -> Optional[MenuState]:
        """Получить текущее состояние меню пользователя.

        Аргументы:
            user_id: ID пользователя Discord

        Возвращает:
            Текущее состояние MenuState или None, если не найдено
        """
        return self.user_states.get(user_id)

    def start_menu(self, user_id: int, channel_id: int) -> None:
        """Начать новую сессию меню для пользователя.

        Аргументы:
            user_id: ID пользователя Discord
            channel_id: ID канала Discord
        """
        self.user_states[user_id] = MenuState.EMBED_TEXT
        self.user_data[user_id] = {}
        self.user_channels[user_id] = channel_id

    def check_channel(self, user_id: int, channel_id: int) -> bool:
        """Проверить, совпадает ли канал с сохраненным."""
        return self.user_channels.get(user_id) == channel_id

    def _get_next_state_and_prompt(
        self, current_state: MenuState
    ) -> Tuple[MenuState, Optional[str]]:
        """Получить следующее состояние и сообщение подсказки на основе текущего состояния.

        Аргументы:
            current_state: Текущее состояние MenuState

        Возвращает:
            Кортеж (следующее_состояние, сообщение_подсказки)
        """
        state_transitions = {
            MenuState.EMBED_TEXT: (
                MenuState.EMBED_CONTENT,
                "Введите содержание embed:",
            ),
            MenuState.EMBED_CONTENT: (
                MenuState.EMBED_PHOTO,
                "Хотите прикрепить фотографию? Если да, отправьте её, если нет, напишите 'нет':",
            ),
            MenuState.EMBED_PHOTO: (MenuState.FINISHED, None),
        }
        return state_transitions.get(current_state, (MenuState.FINISHED, None))

    def process_answer(self, user_id: int, answer: str) -> Optional[str]:
        """Обработать ответ пользователя и вернуть следующую подсказку."""
        if user_id not in self.user_states:
            return None

        current_state = self.user_states[user_id]

        self.user_data[user_id][current_state.name] = answer

        next_state, prompt = self._get_next_state_and_prompt(current_state)
        self.user_states[user_id] = next_state

        return prompt

    def get_summary_embed(self, user_id: int) -> discord.Embed:
        """Создать сводное embed-сообщение из данных пользователя.

        Аргументы:
            user_id: ID пользователя Discord

        Возвращает:
            Discord embed с информацией о пользователе
        """
        data = self.user_data.get(user_id, {})

        embed = discord.Embed(
            title=data.get("EMBED_TEXT", "(заголовок задания)"),
            description=data.get("EMBED_CONTENT", "(описание задания)"),
            color=discord.Color.gold(),
        )

        for key, value in data.items():
            if not value:
                continue

            if key == "EMBED_PHOTO":
                embed.set_image(url=value)

            elif key == "EMBED_TEXT":
                embed.title = value
            elif key == "EMBED_CONTENT":
                if isinstance(value, str) and value.lower() != "нет":
                    embed.description = value

        return embed

    def get_task_complete_embed(self) -> discord.Embed:
        return discord.Embed(
            title="✅ Задание выполнено",
            color=discord.Color.green(),
        )

    def add_message_to_delete(self, user_id: int, message: discord.Message) -> None:
        """Добавить сообщение в список на удаление"""
        if user_id not in self.messages_to_delete:
            self.messages_to_delete[user_id] = []
        self.messages_to_delete[user_id].append(message)

    async def delete_user_messages(self, user_id: int) -> None:
        """Удалить все сообщения пользователя"""
        await asyncio.sleep(2)
        if user_id not in self.messages_to_delete:
            return

        messages = self.messages_to_delete[user_id]
        if not messages:
            return

        channel = messages[0].channel
        try:
            if isinstance(channel, discord.TextChannel):
                await channel.delete_messages(messages)
            else:
                for msg in messages:
                    try:
                        await msg.delete()
                    except discord.errors.HTTPException:
                        pass
        except discord.errors.HTTPException:

            for msg in messages:
                try:
                    await msg.delete()
                except discord.errors.HTTPException:
                    pass

        self.messages_to_delete[user_id] = []
