from core.ports.storage_port import StoragePort
import boto3
import os
import io
import zipfile

class S3Adapter(StoragePort):
    def __init__(self):
        self.client = boto3.client('s3')
    
    def download_file(self, bucket_name, file_key, local_path):
        try:
            print("Baixando o arquivo:", file_key)
            self.client.download_file(bucket_name, file_key, local_path)
            print("Arquivo baixado com sucesso no caminho:", local_path)
        except Exception as e:
            raise Exception("Erro ao baixar o arquivo:", str(e))
    
    def upload_extracted_frames(self, frames_folder, output_bucket, output_folder):
        try:
            # Send the frames to the S3
            print("Enviando os frames para o S3")
            for frame_file in os.listdir(frames_folder):
                frame_path = os.path.join(frames_folder, frame_file)
                s3_key = f"{output_folder}/{frame_file}"
                self.client.upload_file(frame_path, output_bucket, s3_key)
                os.remove(frame_path)  # Removes the local frame after the upload

            os.rmdir(frames_folder)
            print("Frames enviados para o S3.")
        except Exception as e:
            raise Exception("Erro ao enviar o arquivo para o S3:", str(e))
    
    """
    Upload the video's frames in the Bucket

    Parameters:
    output_bucket (string): The Output Bucket name.
    frames_folder (string): The folder where the frames are stored in the bucket
    output_zip_key (string): Name of the output zip file in the Bucket

    Returns:
    void
    """
    def zip_frames_on_s3(self, output_bucket, frames_folder, output_zip_key):
        zip_buffer = io.BytesIO()  # Creates a buffer in memory for the file ZIP

        try:
            print("Zipando frames no S3")
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # List the frames in the S3
                response = self.client.list_objects_v2(Bucket=output_bucket, Prefix=frames_folder)
                for obj in response.get('Contents', []):
                    frame_key = obj['Key']
                    frame_obj = self.client.get_object(Bucket=output_bucket, Key=frame_key)
                    frame_data = frame_obj['Body'].read()
                    zipf.writestr(frame_key.split('/')[-1], frame_data)  # Adiciona o frame ao ZIP

            # Envia o arquivo ZIP de volta para o S3
            zip_buffer.seek(0)
            self.client.put_object(Bucket=output_bucket, Key=output_zip_key, Body=zip_buffer)
            print("Frames zipados no S3.")
        except Exception as e:
            raise Exception("Erro ao zipar frames no S3:", str(e))
    
    def generate_presigned_url(self, output_bucket, file_key, expiration):
        try:
            print("Gerando URL de download para:", file_key)
            zip_url = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": output_bucket, "Key": file_key},
                ExpiresIn=expiration  # URL válido por 24 horas
            )
            print("Arquivo ZIP disponível em:", zip_url)
            return zip_url
        except Exception as e:
            raise Exception("Erro ao gerar URL de download:", str(e))