import os
from main.core.ports.storage_port import StoragePort
from main.core.ports.ffmpeg_port import FFmpegPort
from main.core.ports.messaging_port import MessagingPort
from main.core.utils.messages_utils.type_message import TypeMessage

TEMPORARY_FOLDER = "/tmp/"
ROOT_FRAMES_FOLDER = TEMPORARY_FOLDER + "frames/"
SQS_URL = os.environ['SQS_URL']


class VideoProcessor:
    def __init__(self, storage: StoragePort, messaging: MessagingPort, ffmpeg: FFmpegPort):
        self.storage = storage
        self.messaging = messaging
        self.ffmpeg = ffmpeg


    def process_video(self, input_bucket: str, output_bucket: str, file_key: str):
        folder_name = file_key.split('/')[0]
        file_name = file_key.split('/')[1]
        
        print("Iniciando processamento do arquivo:", file_key)
        try:

            # Create a local folder for storing frames: /tmp/frames/user_uuid/
            new_folder_name = ROOT_FRAMES_FOLDER + folder_name
            self.create_frames_folder(new_folder_name)

            local_video_path = new_folder_name + "/" + file_name
            self.storage.download_file(input_bucket, file_key, local_video_path)

            self.ffmpeg.extract_frames(local_video_path, new_folder_name)

            output_zip_key = folder_name + "/" + file_name + ".zip"
        
            self.storage.upload_extracted_frames(frames_folder=new_folder_name, output_bucket=output_bucket, output_folder=folder_name)

            self.storage.zip_frames_on_s3(output_bucket=output_bucket, frames_folder=folder_name, output_zip_key=output_zip_key)

            url_expiration = 3600*24 # 1 day
            self.storage.generate_presigned_url(output_bucket=output_bucket, file_key=file_key + ".zip", expiration=url_expiration)

            message = self.messaging.build_message(message="Arquivo zipado com sucesso!", type_message=TypeMessage.SUCCESS, user_uuid=file_key, file=file_key + ".zip")
            self.messaging.send_message(SQS_URL, message)

        except Exception as e:
            self.messaging.build_message(message=str(e), type_message=TypeMessage.ERROR, user=file_key, file=file_key + ".zip")
            self.messaging.send_message(SQS_URL, message)
            raise Exception("Erro ao processar o arquivo:", str(e))
        
    
    def create_frames_folder(self, folder_name):
        try:
            os.makedirs(folder_name, exist_ok=True)
            print("Diretório para frames criado com sucesso: ", folder_name)
        except Exception as e:
            raise Exception(f"Erro ao criar diretório para frames: {str(e)}")