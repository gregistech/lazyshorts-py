# LazyShorts

A command-line tool to convert long-form videos into multiple short-form videos, with burned-in text and subtitles.
It also cuts out unwanted silence.


## Preview


### Original video

https://user-images.githubusercontent.com/29675001/210073372-f2a3fa63-29c2-4bc0-ab03-31188a772021.mp4


### Result (with manual subtitle correction)

https://user-images.githubusercontent.com/29675001/210073848-09bcd7b7-6a86-4114-ab0b-72ddf674e298.mp4


### Result (without manual subtitle correction)

As you can see, in Hungarian the `medium` model works quite well: considering the bad quality of my input. 
The `large` model could be even better: **if** you have the hardware. :)

https://user-images.githubusercontent.com/29675001/210073868-f650cef7-093c-4260-9407-c6bc7de1b59e.mp4


## Notes


### Arguments

See `lazyshorts -h`


### Subtitles

I use Whisper to transcribe audible voices to text. 

Obviously with non-english languages the accuracy can be lower: you can help that by...
- ...using a different (for now, only Whisper) model (be wary, the `medium` model is hard to run even with 8GBs of RAM.)
- ...editing subtitles manually from segment to segment. (`{lazyshorts-py} e1 2 45 78`...)


### Not tested

- I don't know if running Whisper on GPU works, you could try CUDA. See `--whisper_device` and PyTorch/Whisper documentation. Also, get the CUDA enabled PyTorch as I define the CPU one in the `requirements.txt`.


### Known issues

- `moviepy` is largely unmaintained at the moment, somehow it collides with `multiprocessing` and the whole tool can crash-and-burn (as in, freeze) and you'll have to force exit. The renders still completed in my testing.
- We could use `rich` to have nice progress bars, as currently you have to manually poll the status of the renders.
- Cropping is just arbitrary: I wanted to use MediaPipe. It's not easy to even get it to run, but my resources were not enough. Maybe a less demanding model or cloud is needed?
- Don't combine segments that are less than `end_time`, you'll get an exception.
