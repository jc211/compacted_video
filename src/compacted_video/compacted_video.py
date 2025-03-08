from pathlib import Path
import tempfile
import os
import time

from compacted_video.utils import concatenate_videos
from torchcodec.decoders import VideoDecoder


if __name__ == "__main__":
    pass


class CompactedVideoBuilder:
    """
    Creates one big video from smaller videos so that it can be indexed with one decoder in one shot.
    """

    def __init__(self):
        self.video_paths = []
        self.all_timestamps = []

    def add_video(self, timestamps: list[float], path: Path | str):
        path = Path(path)
        self.video_paths.append(path)
        self.all_timestamps.append(timestamps)

    def finalize(self):
        temp_output_path = os.path.join(
            tempfile.gettempdir(), f"temp_concat_{int(time.time())}.mp4"
        )
        concatenate_videos(self.video_paths, Path(temp_output_path))
        decoder = VideoDecoder(temp_output_path)
        os.remove(temp_output_path)
        return CompactedVideo(decoder, self.all_timestamps)


class CompactedVideo:
    def __init__(self, decoder: VideoDecoder, all_timestamps: list[float]):
        self.decoder = decoder
        self.all_timestamps = all_timestamps
