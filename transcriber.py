import whisper

class Transcriber:
    def __init__(self, model = "base", device = "cpu"):
        self.model = whisper.load_model(model, device = device)

    def audio_to_segments(self, audio):
        return self.model.transcribe(audio)["segments"]
