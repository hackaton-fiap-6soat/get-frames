from abc import ABC, abstractmethod

class FFmpegPort(ABC):
    @abstractmethod
    def extract_frames(self, video_path: str, output_folder: str) -> None:
        pass