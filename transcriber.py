import whisper

class Transcriber:
    def __init__(self, model = "base", device = "cpu"):
        self._model = whisper.load_model(model, device = device)

    # FIXME: this means our transcriber will not be able to be reused
    # FIXME: actually, this doesn't free up the memory, we could use a process that dies...
    # I've not seen any official functions to just free up the model from memory...
    def clear(self):
        del self._model

    def audio_to_segments(self, audio):
        return self._model.transcribe(audio)["segments"]
