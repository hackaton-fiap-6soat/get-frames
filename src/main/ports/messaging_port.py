from abc import ABC, abstractmethod
from main.core.utils.messages_utils.type_message import TypeMessage

class MessagingPort(ABC):
    @abstractmethod
    def send_message(self, queue_url: str, message: dict) -> None:
        pass
    
    @abstractmethod
    def build_message(self, message: str, type_message: TypeMessage, user_uuid: str, file: str) -> dict:
        pass