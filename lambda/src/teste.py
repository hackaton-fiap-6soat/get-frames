import ffmpeg
import os

def convert_mkv_to_mp4(input_file, output_file):
    try:
        # Converte o vídeo usando ffmpeg
        # ffmpeg.input(input_file).output(output_file, codec="copy").run()
        ffmpeg.input(input_file).output(output_file, vcodec="libx264", acodec="aac").run()
        print(f"Arquivo convertido com sucesso: {output_file}")
    except ffmpeg.Error as e:
        print("Erro durante a conversão:", e)

# Exemplo de uso
input_file = os.path.abspath("teste.mkv")
convert_mkv_to_mp4(input_file, "saida.mp4")