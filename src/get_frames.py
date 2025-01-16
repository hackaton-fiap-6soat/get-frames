import subprocess
import os

def extract_frames(video_path, output_folder):
    # Certifique-se de que o diretório de saída existe
    os.makedirs(output_folder, exist_ok=True)

    # Define o padrão de saída para os arquivos de imagem
    output_pattern = os.path.join(output_folder, "frame_%04d.jpeg")

    # Comando FFmpeg para extrair frames
    command = [
        "ffmpeg",
        "-i", video_path,  # Vídeo de entrada
        output_pattern,  # Arquivo de saída com padrão
        "-q:v", "2"  # Qualidade do vídeo (2 é alta qualidade)
    ]

    try:
        # Executa o comando FFmpeg
        subprocess.run(command, check=True)
        print(f"Frames extraídos com sucesso para o diretório: {output_folder}")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o comando: {e}")

# Exemplo de uso
extract_frames("video.mp4", "frames_output")