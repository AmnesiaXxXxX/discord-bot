from typing import List



class WaitingAnswer:
    def __init__(self) -> None:
        self.waiting_users: List[int] = []
    
    def add_user(self, user_id: int) -> None:
        if user_id not in self.waiting_users:
            self.waiting_users.append(user_id)

    def remove_user(self, user_id: int) -> None:
        if user_id in self.waiting_users:
            self.waiting_users.remove(user_id)

    def is_waiting(self, user_id: int) -> bool:
        return user_id in self.waiting_users