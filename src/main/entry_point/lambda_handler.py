from main.adapters.sqs_adapters.user_sqs_adapter import UserSQSAdapter
from main.adapters.sqs_adapters.process_tracking_sqs_adapter import ProcessTrackingSQSAdapter
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

        user_sqs_adapter = UserSQSAdapter()
        tracking_sqs_adapter = ProcessTrackingSQSAdapter()
        s3 = S3Adapter()
        ffmpeg = FFmpegAdapter()
        video_processor = VideoProcessor(s3, user_sqs_adapter, tracking_sqs_adapter, ffmpeg)
        
        video_processor.process_video(INPUT_BUCKET, OUTPUT_BUCKET, file_key)
    except Exception as e:
        raise Exception(f"Não foi possível concluir o processamento do video: {e}")