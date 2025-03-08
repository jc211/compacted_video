from pathlib import Path

from compacted_video.utils import concatenate_videos


if __name__ == "__main__":
    concatenate_videos(
        [
            Path("tests/videos/1.mp4"),
            Path("tests/videos/2.mp4"),
        ],
        Path("tests/videos/output.mp4"),
    )
