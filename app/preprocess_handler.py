
import subprocess

from queue import Empty
from multiprocessing import Process, Queue

class PreprocessHandler:
    def __init__(self, work_dir_handler, transcriber):
        self._work_dir_handler = work_dir_handler
        self._transcriber = transcriber

    def _cut_silence(self, video):
        fast = self._work_dir_handler.create_file("fast.mp4")
        # NOTE: clean up as auto-editor leaves this behind...
        self._work_dir_handler.register_name("ae-22w46a")
        subprocess.run(
            [
                "auto-editor", 
                video, 
                "--no-open", 
                "--temp-dir", self._work_dir_handler.create_dir("auto-editor"), 
                "-o", fast
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT
        )
        return fast
    def _v_to_a(self, video):
        audio = self._work_dir_handler.create_file("audio.wav")
        subprocess.run(["ffmpeg", "-i", video, audio],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT)
        return audio
    def _preprocess_video(self, original_video):
        video = self._cut_silence(original_video)
        audio = self._v_to_a(video)
        return video, audio
    def process_video(self, video):
        video, audio = self._preprocess_video(video)
        segments = self._transcriber.audio_to_segments(audio)
        self._transcriber.clear()
        return video, segments
