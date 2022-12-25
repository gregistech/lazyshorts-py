import whisper
import os
import subprocess
import srt
from datetime import timedelta
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.fx.all import crop
import editor

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

video = "project.mp4"
fast = cut_silence(video)

audio = v_to_a(fast)
model = whisper.load_model("base", device = "cpu")
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
        original = VideoFileClip(fast)
        selected_segments = [segments[int(i)] for i in inp.split()]
        clips = []
        subs = []
        last_end = 0
        for i, segment in enumerate(selected_segments):
            end = segment['end'] if segment['end'] < original.end else original.end # NOTE: whisper can return longer timestamps than original duration...
            end_rel = last_end + (end - segment["start"])
            clips.append(original.subclip(segment['start'], end))
            subs.append(srt.Subtitle(i, timedelta(seconds=last_end), timedelta(seconds=end_rel), segment["text"]))
            last_end = end_rel
        concat = concatenate_videoclips(clips)
        
        # NOTE: my original idea was to use mediapipe:autoflip, but I don't have enough ram :) this will be enough for a prototype
        (w, h) = concat.size
        cropped = crop(concat, x_center = w/2, y_center = h/2, width = 607, height = 1080)
        
        end_time = 5
        end = concatenate_videoclips([cropped.subclip(0, cropped.end - end_time), CompositeVideoClip([cropped.subclip(cropped.end - end_time, cropped.end), TextClip("A teljes videó megtalálható fő csatornáimon!", fontsize = 48, method = "caption", font = "Arial", color="white").set_duration(end_time).set_pos("center", "center")])])
        end.write_videofile("end.mp4", logger=None) # NOTE: moviepy buggy, can't compose properly AND can't use subtitles correctly
        #end = VideoFileClip("end.mp4")

        #txt_gen = lambda txt: TextClip(txt, font='Arial', fontsize=36, color='white', method="caption", align = "south")
        #subtitle = CompositeVideoClip([end, SubtitlesClip(subs, txt_gen).set_position(("center", 800))])
        
        with open("subs.srt", "w") as file:
            file.write(srt.compose(subs))

        subprocess.run(["ffmpeg", "-i", "end.mp4", "-vf", "subtitles=subs.srt:force_style='Alignment=2,MarginV=50,Fontsize=12'", "-c:a", "copy", f"shorts{count}.mp4"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT)

        #final = VideoFileClip("subtitle.mp4")
        #final.write_videofile(f"shorts{count}.mp4", logger=None)
        count += 1
            


