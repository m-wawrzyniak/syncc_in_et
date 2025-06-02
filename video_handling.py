import subprocess
import os

# Ścieżka do folderu z wideo
folder = "C:/Users/Badania/PycharmProjects/et_procedure/videos"  # Zmień na swój folder
output_prefix = "norm_"

for filename in os.listdir(folder):
    if filename.endswith(".mp4"):
        input_path = os.path.join(folder, filename)
        output_path = os.path.join(folder, f"{output_prefix}{filename}")

        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
            "-c:v", "copy",
            output_path
        ]

        print("Normalizing:", filename)
        subprocess.run(cmd)
