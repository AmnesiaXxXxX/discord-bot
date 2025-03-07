import discord
from enum import Enum
from typing import Dict, Optional, Literal


class MenuState(Enum):
    WAITING_NAME = 1
    WAITING_AGE = 2
    WAITING_CITY = 3
    WAITING_PHOTO = 4
    FINISHED = 5


class MenuManager:
    def __init__(self):
        self.user_states: Dict[int, MenuState] = {}
        self.user_data: Dict[int, Dict[str, str]] = {}

    def start_menu(self, user_id: int):
        self.user_states[user_id] = MenuState.WAITING_NAME
        self.user_data[user_id] = {}

    def get_current_state(self, user_id: int) -> Optional[MenuState]:
        return self.user_states.get(user_id)

    def process_answer(self, user_id: int, answer: str) -> Optional[str]:
        if user_id not in self.user_states:
            return None

        current_state = self.user_states[user_id]

        if current_state == MenuState.WAITING_NAME:
            self.user_data[user_id]["name"] = answer
            self.user_states[user_id] = MenuState.WAITING_AGE
            return "Введите ваш возраст:"

        elif current_state == MenuState.WAITING_AGE:
            self.user_data[user_id]["age"] = answer
            self.user_states[user_id] = MenuState.WAITING_CITY
            return "Введите ваш город:"

        elif current_state == MenuState.WAITING_CITY:
            self.user_data[user_id]["city"] = answer
            self.user_states[user_id] = MenuState.WAITING_PHOTO
            return "Хотите прикрепить фотографию? Если да, отправьте её, если нет, напишите 'нет':"

        elif current_state == MenuState.WAITING_PHOTO:
            if answer.lower() != "нет":
                self.user_data[user_id]["photo"] = answer
            self.user_states[user_id] = MenuState.FINISHED
            return None

    def get_summary_embed(self, user_id: int) -> discord.Embed:
        data = self.user_data[user_id]
        embed = discord.Embed(
            title=f"📝 Информация о пользователе: {data['name']}",
            description=f"📅 Возраст: {data['age']}\n🏙️ Город: {data['city']}",
            color=discord.Color.gold(),
        )
        if "photo" in data:
            embed.set_image(url=data["photo"])
        return embed
