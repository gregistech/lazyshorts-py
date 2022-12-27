import subprocess

from transcriber import Transcriber

import editor

import srt
from datetime import timedelta

from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.fx.all import crop

import tempfile
import shutil

import uuid
from pathlib import Path
import os
class WorkingDirectoryManager:
    def __init__(self, work_dir = False):
        self._work_dir = work_dir
        self._is_work_dir_created = work_dir
        self._is_work_dir_set_by_user = work_dir
        self._registered_files = []

    @property
    def work_dir(self):
        if not self._is_work_dir_created:
            if self._is_work_dir_set_by_user:
                Path(self._work_dir).mkdir(parents=True, exist_ok=True)
            else:
                self.work_dir = tempfile.mkdtemp() 
        return self._work_dir
    @work_dir.setter
    def work_dir(self, work_dir):
        self._work_dir = work_dir + "/"

    def __del__(self):
        self._cleanup_work_dir()

    def _delete_registered_files(self):
        for file in self._registered_files:
            os.remove(file)

    def _cleanup_work_dir(self):
        if self._is_work_dir_set_by_user:
            PipelineHandler._delete_registered_files()
        else:
            shutil.rmtree(self.work_dir)

    def create_file(self, file):
        new_file = self.work_dir + str(uuid.uuid4()) + file
        self._registered_files.append(new_file)
        return new_file

class PipelineHandler:
    def __init__(self, original_video_file = False):
        self._video = ""
        self.segments = ""
        self._original_video_file = ""
        self.transcriber = Transcriber()
        self.work_dir_handler = WorkingDirectoryManager()
        if original_video_file:
            self.set_original_video_file(original_video_file)
    
    def _cut_silence(self, video):
        fast = self.work_dir_handler.create_file("file.mp4")
        # FIXME: temp dir is not picked up (it works on the command-line...)
        proc = subprocess.run(["auto-editor", video, "--no-open", "--temp-dir", self.work_dir_handler.work_dir, "-o", fast],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT)
        print(proc)
        return fast
    def _v_to_a(self, video):
        clip = VideoFileClip(video)
        audio = self.work_dir_handler.create_file("audio.wav")
        clip.audio.write_audiofile(audio, logger=None)
        return audio
    def _preprocess_video(self, original_video):
        video = self._cut_silence(original_video)
        audio = self._v_to_a(video)
        return video, audio

    def _process_video(self, video):
        video, audio = self._preprocess_video(video)
        return video, self.transcriber.audio_to_segments(audio)
 
    @property
    def original_video_file(self):
        return self._original_video_file
    @original_video_file.setter
    def original_video_file(self, video_file):
        self._original_video_file = video_file
        self._video, self.segments = self._process_video(video_file)

    # NOTE: whisper can return longer timestamps than original duration...
    def _get_segment_end(self, segment):
        original = VideoFileClip(self._video)
        return segment['end'] if segment['end'] < original.end else original.end
    def _get_segment_relative_end(self, segment, last_end):
        return last_end + (self._get_segment_end(segment) - segment["start"])

    def _segment_to_clip(self, segment):
        original = VideoFileClip(self._video)
        return original.subclip(segment['start'], self._get_segment_end(segment))
    def _segment_to_sub(self, segment, i, last_end, current_end):
        original = VideoFileClip(self._video)
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
    def _segments_to_clip_and_subs(self, selected):
        clips = []
        subs = []
        self._enumerate_on_segments(selected,
                lambda segment, i, last_end, current_end: 
                    [
                        clips.append(self._segment_to_clip(segment)), 
                        subs.append(self._segment_to_sub(segment, i, last_end, current_end))
                    ]
        )
        return concatenate_videoclips(clips), subs

    def _crop_clip(clip):
        (w, h) = clip.size
        return crop(clip, x_center = w/2, y_center = h/2, width = 607, height = 1080)
    def _clip_to_file(self, clip):
        clip_file = self.work_dir_handler.create_file("end.mp4")
        clip.write_videofile(clip_file, logger=None) 
        return clip_file
    def _overlay_end_text_on_clip(clip, end_time = 5):
        return concatenate_videoclips([clip.subclip(0, clip.end - end_time), CompositeVideoClip([clip.subclip(clip.end - end_time, clip.end), TextClip("A teljes videó megtalálható fő csatornáimon!", fontsize = 48, method = "caption", font = "Arial", color="white").set_duration(end_time).set_pos("center", "center")])])

    def _burn_in_subs_to_file(self, file, sub_file):
        subbed_file = self.work_dir_handler.create_file("subbed.mp4")
        subprocess.run(["ffmpeg", "-y", "-i", file, "-vf", f"subtitles={sub_file}:force_style='Alignment=2,MarginV=50,Fontsize=12'", "-c:a", "copy", subbed_file])#,
            #stdout=subprocess.DEVNULL,
            #stderr=subprocess.STDOUT)
        return subbed_file
    def _subs_to_file(self, subs):
        sub_file = self.work_dir_handler.create_file("subs.srt")
        with open(sub_file, "w") as file:
            file.write(srt.compose(subs))
        return sub_file
    
    def render_file(self, selected, final_file):
        concat, subs = self._segments_to_clip_and_subs(selected)
        cropped = PipelineHandler._crop_clip(concat)
        end_file = self._clip_to_file(PipelineHandler._overlay_end_text_on_clip(cropped))
        subbed_file = self._burn_in_subs_to_file(end_file, self._subs_to_file(subs))
        shutil.move(subbed_file, final_file)
        return final_file
