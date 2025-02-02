from main.adapters.sqs_adapter import SQSAdapter
from main.adapters.s3_adapter import S3Adapter
from main.adapters.ffmpeg_adapter import FFmpegAdapter
from main.core.video_processor import VideoProcessor
import os

INPUT_BUCKET = os.environ['INPUT_BUCKET']
OUTPUT_BUCKET = os.environ['OUTPUT_BUCKET']

def lambda_handler(event, context):
    try:
        print("Recebido evento:", event)
        file_key = event.get('Records')[0].get('s3').get('object').get('key')

        sqs = SQSAdapter()
        s3 = S3Adapter()
        ffmpeg = FFmpegAdapter()
        video_processor = VideoProcessor(s3, sqs, ffmpeg)
        
        video_processor.process_video(INPUT_BUCKET, OUTPUT_BUCKET, file_key)
    except Exception as e:
        raise Exception("Não foi possível concluir o processamento do video:", str(e))