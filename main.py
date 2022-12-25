import subprocess

import whisper
import editor

import srt
from datetime import timedelta

from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.fx.all import crop


def cut_silence(video):
    fast = "fast.mp4"
    #subprocess.run(["auto-editor", video, "--no-open", "-o", fast],
    #        stdout=subprocess.DEVNULL,
    #        stderr=subprocess.STDOUT)
    return fast

def v_to_a(video):
    clip = VideoFileClip(video)
    audio = "audio.wav"
    #clip.audio.write_audiofile(audio, logger=None)
    return audio

def get_segment_end(segment, original):
    return segment['end'] if segment['end'] < original.end else original.end # NOTE: whisper can return longer timestamps than original duration...
def get_segment_relative_end(segment, original, last_end):
    return last_end + (get_segment_end(segment, original) - segment["start"])

def segment_to_clip(segment, original):
    return original.subclip(segment['start'], get_segment_end(segment, original))
def segment_to_sub(segment, original, last_end, i):
    return srt.Subtitle(i, timedelta(seconds=last_end), timedelta(seconds=get_segment_relative_end(segment, original, last_end)), segment["text"])

def enumerate_on_segments(segments, original, f):
    last_end = 0
    for i, segment in enumerate(segments):
        f(i, segment, original, last_end)
        last_end = get_segment_relative_end(segment, original, last_end)

def segments_to_clip_and_subs(segments):
        clips = []
        subs = []
        original = VideoFileClip(fast)
        enumerate_on_segments(segments, 
                original, 
                lambda i, segment, original, last_end: 
                    [
                        clips.append(segment_to_clip(segment, original)), 
                        subs.append(segment_to_sub(segment, original, last_end, i))
                    ]
        )
        return concatenate_videoclips(clips), subs

video = "project.mp4"
print(f"Cutting silence out of video ({video})...")
fast = cut_silence(video)

print(f"Converting video ({fast}) to audio...")
audio = v_to_a(fast)

model = "base"
device = "cpu"
print(f"Loading Whisper model {model} on your {device}...")
model = whisper.load_model(model, device = device)

print(f"Transcribing audio ({audio}) to text segments...")
segments = model.transcribe(audio)["segments"]

run = True
count = 0
while run:
    for segment in segments:
        print(f"{segment['id']}: {segment['start']} -> {segment['end']}")
        print(segment['text'])
        print("---" * 25)
    inp = input("Command: ")
    if inp == "exit":
        run = False
    elif inp[0] == "e":
        selected_segments = [segments[int(i)] for i in inp[1:].split()]
        for segment in selected_segments:
            segment['text'] = editor.edit(contents=segment['text'].encode("UTF-8")).decode("UTF-8")
    else:
        selected_segments = [segments[int(i)] for i in inp.split()]
        
        print("Generating concatenated clip and syncing subtitles...")
        concat, subs = segments_to_clip_and_subs(selected_segments)

        sub_file = "subs.srt"
        print(f"Writing out subtitles to {sub_file}...")
        with open(sub_file, "w") as file:
            file.write(srt.compose(subs))
        
        print("Cropping to size...")
        # NOTE: my original idea was to use mediapipe:autoflip, but I don't have enough ram :) this will be enough for a prototype
        (w, h) = concat.size
        cropped = crop(concat, x_center = w/2, y_center = h/2, width = 607, height = 1080)
        
        print("Putting on end text...")
        end_time = 5
        end = concatenate_videoclips([cropped.subclip(0, cropped.end - end_time), CompositeVideoClip([cropped.subclip(cropped.end - end_time, cropped.end), TextClip("A teljes videó megtalálható fő csatornáimon!", fontsize = 48, method = "caption", font = "Arial", color="white").set_duration(end_time).set_pos("center", "center")])])
        end_file = "end.mp4"
        end.write_videofile(end_file, logger=None) # NOTE: moviepy buggy, can't compose properly AND can't use subtitles correctly
        
        print("Burning-in subtitles...")
        subprocess.run(["ffmpeg", "-i", end_file, "-vf", f"subtitles={sub_file}:force_style='Alignment=2,MarginV=50,Fontsize=12'", "-c:a", "copy", f"shorts{count}.mp4"])#,
                #stdout=subprocess.DEVNULL,
                #stderr=subprocess.STDOUT)
        print(f"Done, wrote to shorts{count}.mp4!")
        count += 1
            


