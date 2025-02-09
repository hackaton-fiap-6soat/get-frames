from abc import ABC, abstractmethod

class MessagingPort(ABC):
    @abstractmethod
    def send_message(self, queue_url: str, message: dict) -> None:
        pass
    
    @abstractmethod
    def build_message(self, message_attributes: dict) -> dict:
        pass