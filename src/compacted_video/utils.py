import os
import subprocess
import tempfile
from pathlib import Path


def concatenate_videos(video_files: list[Path], output_file: Path):
    # Create a temporary file in the system's temp directory
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as temp:
        temp_file_path = temp.name
        for video_file in video_files:
            temp.write(f"file '{video_file.resolve()}'\n")

    cmd = [
        "ffmpeg",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        temp_file_path,
        "-c",
        "copy",
        output_file,
    ]

    try:
        subprocess.run(cmd)
    finally:
        os.remove(temp_file_path)
