import subprocess
import os
import boto3
import os
import subprocess
import io
import zipfile

from utils.utils import zip_frames
s3 = boto3.client('s3')

TEMPORARY_FOLDER = "/tmp/"
ROOT_FRAMES_FOLDER = TEMPORARY_FOLDER + "frames/"
SQS_URL = os.environ['SQS_URL']

ffmpeg_path = os.environ.get("FFMPEG_PATH", "/opt/bin/ffmpeg")

# Quem chama a funcao, vai mandar o caminho do video (S3)

def lambda_handler(event, context):
    print("Recebido evento:", event)
    file_key = event.get('Records')[0].get('s3').get('object').get('key')
    folder_name = file_key.split('/')[0]
    file_name = file_key.split('/')[1]
    try:
        # Obter detalhes do arquivo a partir do evento
        input_bucket_name = os.environ['INPUT_BUCKET']
        output_bucket = os.environ['OUTPUT_BUCKET']

        print(f"Bucket: {input_bucket_name}")
        print(f"File Key: {file_key}")
        print(f"Output Bucket: {output_bucket}")
        
        # /tmp/frames/uuid/
        new_folder_name = ROOT_FRAMES_FOLDER + folder_name
        
        # /tmp/frames/uuid/video.mp4.zip
       # zip_file_path = new_folder_name + "/" + file_name + ".zip"
        
        # Criar diretório para frames
        try:
            os.makedirs(new_folder_name, exist_ok=True)
            print("Diretório para frames criado com sucesso.")
        except Exception as e:
            raise Exception(f"Erro ao criar diretório para frames: {str(e)}")

        local_video_path = f"{new_folder_name}/{file_name}"
        download_file(input_bucket_name, file_key, local_video_path)

        process_video(local_video_path, new_folder_name)


        output_zip_key = folder_name + "/" + file_name + ".zip"
    
        upload_extracted_frames(frames_folder=new_folder_name, output_bucket=output_bucket, output_folder=folder_name)

        zip_frames_on_s3(output_bucket=output_bucket, frames_folder=folder_name, output_zip_key=output_zip_key)

        generate_download_url(output_bucket, file_key + ".zip")


    except Exception as e:
        build_message(message=str(e), type_message=TypeMessage.ERROR, user=file_key, file=file_key + ".zip")
        raise Exception("Erro ao processar o arquivo:", str(e))
    
    message = build_message(message="Arquivo zipado com sucesso!", type_message=TypeMessage.SUCCESS, user=file_key, file=file_key + ".zip")
    send_sqs_message(message)
        
def download_file(bucket_name, file_key, local_path):
    try:
        s3.download_file(bucket_name, file_key, local_path)
        print("Arquivo baixado com sucesso.")
    except Exception as e:
        raise Exception("Erro ao baixar o arquivo:", str(e))
        
        
def process_video(local_video_path, frames_folder):
    if not os.path.exists(local_video_path):
        raise Exception(f"Erro: O arquivo {local_video_path} não existe.")

    try:
        ffmpeg_command = [
            ffmpeg_path,
            "-i", local_video_path,
            os.path.join(frames_folder, "frame_%04d.jpeg"),
            "-q:v", "2",
            "-loglevel", "quiet"  # Aqui está correto
        ]

        subprocess.run(ffmpeg_command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Frames extraídos com sucesso.")
    except Exception as e:
        raise Exception("Erro ao extrair frames:", str(e))
        
def upload_extracted_frames(frames_folder, output_bucket, output_folder):
    try:
        # Envia os frames para o S3
        for frame_file in os.listdir(frames_folder):
            frame_path = os.path.join(frames_folder, frame_file)
            s3_key = f"{output_folder}/{frame_file}"
            s3.upload_file(frame_path, output_bucket, s3_key)
            os.remove(frame_path)  # Remove o frame local após o upload

        # Remove o diretório temporário
        os.rmdir(frames_folder)

        # s3.upload_file(zip_file, output_bucket, file_name)
        # print("Arquivo ZIP enviado para o S3.")
    except Exception as e:
        raise Exception("Erro ao enviar o arquivo para o S3:", str(e))
        
def generate_download_url(output_bucket, file_key):
    try:
        zip_url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": output_bucket, "Key": file_key},
            ExpiresIn=3600*24  # URL válido por 24 horas
        )
        print("Arquivo ZIP disponível em:", zip_url)
        return zip_url
    except Exception as e:
        raise Exception("Erro ao gerar URL de download:", str(e))
        

def send_sqs_message(message):
    sqs = boto3.client('sqs')
    try:
        sqs.send_message(QueueUrl=SQS_URL, **message)
        print("Mensagem enviada para o SQS com sucesso.")
    except Exception as e:
        raise Exception("Erro ao enviar mensagem para o SQS:", str(e))

def build_message(message, type_message, user, file):
    return {
        "MessageBody": message,
        "MessageAttributes": {
            "Type": {
                "StringValue": type_message,
                "DataType": "String"
            },
            "User": {
                "StringValue": user,
                "DataType": "String"
            },
            "File": {
                "StringValue": file,
                "DataType": "String"
            }
        }
    }

class TypeMessage:
    SUCCESS = "success"
    ERROR = "error"

"""
    Upload the video's frames in the Bucket

    Parameters:
    output_bucket (string): The Output Bucket name.
    frames_folder (string): The folder where the frames are stored in the bucket
    output_zip_key (string): Name of the output zip file in the Bucket

    Returns:
    void
"""
def zip_frames_on_s3(output_bucket, frames_folder, output_zip_key):
    zip_buffer = io.BytesIO()  # Cria um buffer em memória para o arquivo ZIP

    try:
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Lista os frames no S3
            response = s3.list_objects_v2(Bucket=output_bucket, Prefix=frames_folder)
            for obj in response.get('Contents', []):
                frame_key = obj['Key']
                frame_obj = s3.get_object(Bucket=output_bucket, Key=frame_key)
                frame_data = frame_obj['Body'].read()
                zipf.writestr(frame_key.split('/')[-1], frame_data)  # Adiciona o frame ao ZIP

        # Envia o arquivo ZIP de volta para o S3
        zip_buffer.seek(0)
        s3.put_object(Bucket=output_bucket, Key=output_zip_key, Body=zip_buffer)
        print("Arquivo ZIP enviado para o S3.")
    except Exception as e:
        raise Exception("Erro ao enviar o arquivo para o S3:", str(e))