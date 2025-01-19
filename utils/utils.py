import shutil
import os

def zip_frames(output_folder, zip_filename):
    shutil.make_archive(zip_filename, 'zip', output_folder)
    print(f"Frames compactados no arquivo: {zip_filename}.zip")