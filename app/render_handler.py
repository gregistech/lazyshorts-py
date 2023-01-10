import subprocess

from enum import Enum, auto

import srt
from datetime import timedelta

import shutil

from ffprobe import FFProbe

class RenderStatus(Enum):
    START = auto()
    SEGMENT_TO_CLIP = auto()
    CROP_CLIP = auto()
    END_CLIP = auto()
    SUB_CLIP = auto()
    MOVE_CLIP = auto()
    FINISH = auto()

class RenderHandler():
    def __init__(self, wdmng, video, render, end_text, end_time):
        self.wdmng = wdmng
        self._video = video
        self._segments, self._final_file = render
        self._end_text, self._end_time = end_text, end_time
    
    def _get_clip_end(self, clip):
        return float(FFProbe(clip).streams[0].duration)

    # NOTE: whisper can return longer timestamps than original duration...
    def _get_segment_end(self, segment):
        end = self._get_clip_end(self._video)
        return segment['end'] if segment['end'] < end else end
    def _get_segment_relative_end(self, segment, last_end):
        return last_end + (self._get_segment_end(segment) - segment["start"])

    def _segment_to_clip(self, segment):
        clip = self.wdmng.create_file("segment.mp4")
        subprocess.run(["ffmpeg", "-y", "-i", self._video, "-ss", str(segment['start']), "-to", str(self._get_segment_end(segment)), clip], 
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT
        )
        return clip
    def _segment_to_sub(self, segment, i, last_end, current_end):
        return srt.Subtitle(i, 
                timedelta(seconds=last_end), 
                timedelta(seconds=current_end), 
                segment["text"])

    def _enumerate_on_segments(self, selected, f):
        end = 0
        for i, segment in enumerate(selected):
            last_end = end
            end = self._get_segment_relative_end(segment, last_end)
            f(segment, i, last_end, end)

    def _concat_clips(self, clips):
        inp = ""
        for clip in clips:
            inp += f"file '{clip}'\n"

        file_list = self.wdmng.create_file("concat.txt")
        with open(file_list, "w") as file:
            file.write(inp)

        file = self.wdmng.create_file("concat.mp4")
        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", file_list, "-c:v", "copy", "-c:a", "copy", file], 
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT
        )
        return file

    def _segments_to_clip_and_subs(self):
        clips = []
        subs = []
        self._enumerate_on_segments(self._segments,
                lambda segment, i, last_end, current_end: 
                    [
                        clips.append(self._segment_to_clip(segment)), 
                        subs.append(self._segment_to_sub(segment, i, last_end, current_end))
                    ]
        )
        return self._concat_clips(clips), subs

    def _crop_clip(self, clip):
        file = self.wdmng.create_file("crop.mp4")
        subprocess.run(["ffmpeg", "-y", "-i", clip, "-filter_complex", "[0]scale=3414:1920,crop=1080:1920", "-c:a", "copy", file], 
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT
        )
        return file
    def _overlay_end_text_on_clip(self, clip, text = "The End", time = 5):
        end = self._get_clip_end(self._video)
        start = end - time
        subs = [
            srt.Subtitle(0, timedelta(seconds=start), timedelta(seconds=end), text)
        ]
        sub_file = self._subs_to_file(subs)
        file = self.wdmng.create_file("end.mp4")
        subprocess.run(["ffmpeg", "-y", "-i", clip, "-vf", f"subtitles={sub_file}:force_style='Alignment=10,Fontsize=24'", "-c:a", "copy", file],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT
        )
        return file

    def _burn_in_subs_to_file(self, file, sub_file):
        subbed_file = self.wdmng.create_file("subbed.mp4")
        subprocess.run(["ffmpeg", "-y", "-i", file, "-vf", f"subtitles={sub_file}:force_style='Alignment=2,MarginV=50,Fontsize=12'", "-c:a", "copy", subbed_file],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT
        )
        return subbed_file
    def _subs_to_file(self, subs):
        sub_file = self.wdmng.create_file("subs.srt")
        with open(sub_file, "w") as file:
            file.write(srt.compose(subs))
        return sub_file
    
    def render_file(self, state):
        state[:] = [RenderStatus.SEGMENT_TO_CLIP, .2]
        concat, subs = self._segments_to_clip_and_subs()
        
        state[:] = [RenderStatus.CROP_CLIP, .4]
        cropped = self._crop_clip(concat)

        state[:] = [RenderStatus.END_CLIP, .6]
        end_file = self._overlay_end_text_on_clip(cropped, self._end_text, self._end_time)

        state[:] = [RenderStatus.SUB_CLIP, .8]
        subbed_file = self._burn_in_subs_to_file(end_file, self._subs_to_file(subs))

        state[:] = [RenderStatus.MOVE_CLIP, .9]
        shutil.move(subbed_file, self._final_file)

        state[:] = [RenderStatus.FINISH, 1]
