import subprocess
import os
import shutil
import boto3
import os
import subprocess
from utils.utils import zip_frames
from urllib.parse import unquote_plus
s3 = boto3.client('s3')

TEMPORARY_FOLDER = "/tmp/"
ROOT_FRAMES_FOLDER = TEMPORARY_FOLDER + "frames/"

# Quem chama a funcao, vai mandar o caminho do video (S3)

def lambda_handler(event, context):
    print("Recebido evento:", event)
    try:
        # Obter detalhes do arquivo a partir do evento
        bucket_name = event['queryStringParameters']['bucket']
        file_key = unquote_plus(event['queryStringParameters']['key'])
        output_bucket = event['queryStringParameters']['output_bucket']
        
        local_video_path = TEMPORARY_FOLDER + os.path.basename(file_key)
        frames_folder = ROOT_FRAMES_FOLDER + file_key
        zip_file_path = ROOT_FRAMES_FOLDER + file_key + ".zip"

        # Baixar o arquivo do S3
        s3.download_file(bucket_name, file_key, local_video_path)
        
        # Criar diretório para frames
        os.makedirs(frames_folder, exist_ok=True)

        # Extrair frames com FFmpeg
        ffmpeg_command = [
            "ffmpeg",
            "-i", local_video_path,
            os.path.join(frames_folder, "frame_%04d.jpeg"),
            "-q:v", "2"
        ]
        subprocess.run(ffmpeg_command, check=True)

        # Compactar os frames em um arquivo ZIP
        zip_frames(frames_folder, zip_file_path)

        # Enviar o arquivo ZIP para o S3
        zip_key = f"processed/{os.path.basename(file_key).split('.')[0]}.zip"
        s3.upload_file(zip_file_path, output_bucket, zip_key)

        # Gerar URL público do S3 (caso o bucket seja público ou você use presigned URLs)
        zip_url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": output_bucket, "Key": zip_key},
            ExpiresIn=3600*24  # URL válido por 24 horas
        )
        
        print("Arquivo ZIP disponível em:", zip_url)

        # return {
        #     "statusCode": 200,
        #     "body": f"Arquivo ZIP disponível em: {zip_url}"
        # }

    except Exception as e:
        # Enviar SQS
        print("Erro ao processar o arquivo:", str(e))