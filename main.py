from render_manager import RenderManager
from preprocess_handler import PreprocessHandler
from working_directory_manager import WorkingDirectoryManager
from transcriber import Transcriber
from ui import UI

import argparse

def main():
    if __name__ == "main":
        NAME = "lazyshorts-py"
        DESC = "A command to convert long-form videos into multiple short-form videos, with burned-in text and subtitles."

        parser = argparse.ArgumentParser(prog=NAME, description=DESC)

        parser.add_argument("--work_dir", 
                help = "The directory where the tool should work in.", 
                default = False
        )

        parser.add_argument("--whisper_model", 
                type = str, 
                help = "The model which Whisper should use.", 
                choices = ["tiny", "tiny.en", "base", "base.en", "small", "small.en", "medium", "medium.en", "large"],
                default = "small"
        )
        parser.add_argument("--whisper_device", 
                type = str, 
                help = "The device which Whisper should use.", 
                # TODO: choices = ?, what can be used here? I never tried GPU
                default = "cpu"
        )

        parser.add_argument("--end_time", 
                help = "The n last seconds when the tool should burn-in the end_text.", 
                type=int,
                default=5
        )

        parser.add_argument("file", 
                help = "The file on which the tool should work on."
        )

        parser.add_argument("end_text", 
                help = "The text that will be burnt into the specified end_time last seconds.",
                default = "The End"
        )

        args = parser.parse_args()

        work_dir = args.work_dir
        wdmng = WorkingDirectoryManager(work_dir)
        
        model = args.whisper_model
        device = args.whisper_device
        transcriber = Transcriber(model, device)

        preprocess_handler = PreprocessHandler(wdmng, transcriber)
        end_text = args.end_text
        end_time = args.end_time
        rdmng = RenderManager(wdmng, preprocess_handler, end_text, end_time)
        
        file = args.file
        UI(NAME, file, rdmng)
