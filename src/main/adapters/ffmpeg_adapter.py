from main.ports.ffmpeg_port import FFmpegPort
import os
import subprocess

ffmpeg_path = os.environ.get("FFMPEG_PATH", "/opt/bin/ffmpeg")


class FFmpegAdapter(FFmpegPort):
    def extract_frames(self, video_path: str, output_folder: str) -> None:
        try:
            print("Iniciando a extração de frames...")
            if not os.path.exists(video_path):
                raise Exception(f"Erro: O arquivo {video_path} não existe.")

            ffmpeg_command = [
                ffmpeg_path,
                "-i", video_path,
                os.path.join(output_folder, "frame_%04d.jpeg"),
                "-q:v", "2",
                "-loglevel", "quiet"  # Aqui está correto
            ]

            subprocess.run(ffmpeg_command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("Frames extraídos com sucesso.")
        except Exception as e:
            raise Exception("Erro ao extrair frames:", str(e))