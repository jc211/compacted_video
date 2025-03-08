from pathlib import Path

from compacted_video.compacted_video import CompactedVideoBuilder


if __name__ == "__main__":
    builder = CompactedVideoBuilder()
    builder.add_video(
        [],
        "tests/videos/1.mp4",
    )
    builder.add_video(
        [],
        "tests/videos/2.mp4",
    )
    builder.finalize()
