from abc import ABC, abstractmethod

class StoragePort(ABC):
    @abstractmethod
    def download_file(self, bucket_name: str, file_key: str, local_path: str) -> None:
        pass

    @abstractmethod
    def upload_file(self, bucket_name: str, file_key: str, local_path: str) -> None:
        pass

    @abstractmethod
    def list_files(self, bucket_name: str, prefix: str) -> list:
        pass

    @abstractmethod
    def generate_presigned_url(self, bucket_name: str, file_key: str, expiration: int) -> str:
        pass
    
    @abstractmethod
    def upload_extracted_frames(self, frames_folder: str, output_bucket: str, output_folder: str) -> None:
        pass
    
    @abstractmethod
    def zip_frames_on_s3(self, output_bucket: str, frames_folder: str, output_zip_key: str) -> None:
        pass