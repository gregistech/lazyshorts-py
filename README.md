# LazyShorts

A command-line tool to convert long-form videos into multiple short-form videos, with burned-in text and subtitles.


## Arguments

See `lazyshorts -h`


## Subtitles

We use Whisper to transcribe audible voices to text. 

Obviously with non-english languages the accuracy can be lower: you can help that by...
- ...using a different (for now, only Whisper) model (be wary, the `medium` model is hard to run even with 8GBs of RAM.)
- ...editing subtitles manually from segment to segment. (`{lazyshorts-py} e1 2 45 78`...)


## Not tested
- I don't know if running Whisper on GPU works, you could try CUDA. See `--whisper_device` and PyTorch/Whisper documentation.


## Known issues

- `moviepy` is largely unmaintained at the moment, somehow it collides with `multiprocessing` and the whole tool can crash-and-burn (as in, freeze) and you'll have to force exit. The renders still completed in my testing.
- We could use `rich` to have nice progress bars, as currently you have to manually poll the status of the renders.
- Cropping is just arbitrary: I wanted to use MediaPipe. It's not easy to even get it to run, but my resources were not enough. Maybe a less demanding model or cloud is needed?
