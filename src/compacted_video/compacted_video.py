from pathlib import Path
import tempfile
import os
import time
import numpy as np
import torch
from concurrent.futures import ThreadPoolExecutor

from compacted_video.utils import concatenate_videos
from torchcodec.decoders import VideoDecoder


if __name__ == "__main__":
    pass


class CompactedVideoBuilder:
    """
    Creates one concatenated video from multiple source videos for efficient parallel decoding.
    """

    def __init__(self, num_decoders: int = 4):
        self.video_paths = []
        self.num_decoders = num_decoders

    def add_video(self, path: Path | str):
        """Add a video file to be concatenated."""
        self.video_paths.append(Path(path))

    def finalize(self) -> "CompactedVideo":
        """Build and return a CompactedVideo instance with the concatenated videos."""
        if not self.video_paths:
            raise ValueError("No videos added to builder")

        # Create temporary concatenated video
        temp_output_path = (
            Path(tempfile.gettempdir()) / f"concat_{int(time.time())}.mp4"
        )
        concatenate_videos(self.video_paths, temp_output_path)
        res = CompactedVideo(temp_output_path, num_decoders=self.num_decoders)
        temp_output_path.unlink()
        return res


class CompactedVideo:
    def __init__(self, video_path: Path | str, num_decoders: int = 4):
        self.video_path = Path(video_path)
        # Create multiple decoders for parallel processing
        self.decoders = [
            VideoDecoder(str(self.video_path), device="cuda", dimension_order="NHWC")
            for _ in range(num_decoders)
        ]
        self.executor = ThreadPoolExecutor(max_workers=num_decoders)

    def __del__(self):
        """Clean up the temporary concatenated video file and shutdown executor."""
        self.executor.shutdown()
        if self.video_path.exists():
            self.video_path.unlink()

    def _process_batch(self, decoder_idx: int, frame_indices: np.ndarray):
        """Process a batch of frames using the specified decoder."""
        if len(frame_indices) == 0:
            return None
        return self.decoders[decoder_idx].get_frames_at(frame_indices.tolist()).data

    def get_frames_at(self, timestamps: np.ndarray):
        # timestamps is (..., 1)
        # returns (..., H, W, 3) as torch tensor on GPU

        # Flatten the input timestamps array
        flat_timestamps = timestamps.reshape(-1)
        num_frames = len(flat_timestamps)

        # Split work among decoders
        frames_per_decoder = (num_frames + len(self.decoders) - 1) // len(self.decoders)
        frame_splits = [
            flat_timestamps[i : i + frames_per_decoder]
            for i in range(0, num_frames, frames_per_decoder)
        ]

        # Submit tasks to thread pool
        futures = []
        for decoder_idx, frame_indices in enumerate(frame_splits):
            future = self.executor.submit(
                self._process_batch, decoder_idx, frame_indices
            )
            futures.append(future)

        # Gather results in order
        results = []
        for future in futures:
            result = future.result()
            if result is not None:
                results.append(result)

        # Concatenate results and reshape back to original dimensions
        all_frames = torch.cat(results, dim=0)
        return all_frames
