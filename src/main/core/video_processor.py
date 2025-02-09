import os
from main.ports.storage_port import StoragePort
from main.ports.ffmpeg_port import FFmpegPort
from main.ports.messaging_port import MessagingPort

TEMPORARY_FOLDER = "/tmp/"
ROOT_FRAMES_FOLDER = TEMPORARY_FOLDER + "frames/"
USER_SQS_URL = os.environ['USER_SQS_URL']
PROCESS_TRACKING_SQS_URL = os.environ['PROCESS_TRACKING_SQS_URL']

class VideoProcessor:
    def __init__(self, storage: StoragePort, user_sqs: MessagingPort, tracking_sqs: MessagingPort, ffmpeg: FFmpegPort):
        self.storage = storage
        self.user_sqs = user_sqs
        self.tracking_sqs = tracking_sqs
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
            zip_url =self.storage.generate_presigned_url(output_bucket=output_bucket, file_key=file_key + ".zip", expiration=url_expiration)

            user_message_attributes = {
                "id_usuario": folder_name,
                "link_arquivo": zip_url
            }

            message = self.user_sqs.build_message(user_message_attributes)
            self.user_sqs.send_message(USER_SQS_URL, message)

            tracking_message_attributes = {
                "id_usuario": folder_name,
                "processo": "geracao",
                "nome_arquivo": file_name,
                "status": "ok"
            }
            tracking_message = self.tracking_sqs.build_message(tracking_message_attributes)
            self.tracking_sqs.send_message(PROCESS_TRACKING_SQS_URL, tracking_message)

        except Exception as e:
            user_message_attributes = {
                "id_usuario": folder_name,
            }
            message = self.user_sqs.build_message(user_message_attributes)
            self.user_sqs.send_message(USER_SQS_URL, message)

            tracking_message_attributes = {
                "id_usuario": folder_name,
                "processo": "geracao",
                "nome_arquivo": file_name,
                "status": "error"
            }
            tracking_message = self.tracking_sqs.build_message(tracking_message_attributes)
            self.tracking_sqs.send_message(PROCESS_TRACKING_SQS_URL, tracking_message)
            raise Exception("Erro ao processar o arquivo:", str(e))
        
    
    def create_frames_folder(self, folder_name):
        try:
            os.makedirs(folder_name, exist_ok=True)
            print("Diretório para frames criado com sucesso: ", folder_name)
        except Exception as e:
            raise Exception(f"Erro ao criar diretório para frames: {str(e)}")