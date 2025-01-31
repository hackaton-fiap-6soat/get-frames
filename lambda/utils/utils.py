import zipfile
import os

def zip_frames(folder_to_zip, zip_filename):
    try:
        """Compacta uma pasta sem manter a estrutura de diretórios"""
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(folder_to_zip):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.basename(file_path)  # Apenas o nome do arquivo, sem diretórios
                    zipf.write(file_path, arcname)
        print(f"Frames compactados no arquivo: {zip_filename}")
    except Exception as e:
        print(f"Erro ao compactar os frames: {str(e)}")