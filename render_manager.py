from render_handler import RenderHandler, RenderStatus

from queue import Queue, Empty
from multiprocessing import Process

class RenderManager():
    def __init__(self, wdmng, preprocess_handler):
        self._wdmng = wdmng
        self._preprocess_handler = preprocess_handler
        self._input_file = ""
        self._video, self.segments = "", []
        self._queue = Queue()
        self._renderers = []
    
    @property
    def input_file(self):
        return self._input_file
    @input_file.setter
    def input_file(self, file):
        self._input_file = file
        self._video, self.segments = self._preprocess_handler.process_video(file)
    
    def get_renderer_states(self):
        return [renderer.state for renderer in self._renderers]

    def add_to_queue(self, render):
        self._queue.put(render)
    
    def _join_finished(self):
        for renderer, process in self._renderers:
            if renderer.state[1] == RenderStatus.FINISH:
                # NOTE: arbitrary number, is it good?
                process.join(timeout=5)

    def _main_loop(self):
        self._render_next()
        self._join_finished()
    
    def _start_execution(self):
        while True:
            self._main_loop()

    def start(self):
        return Process(target=self._start_execution)

    def _render_next(self):
        try:
            render = self._queue.get_nowait()
            renderer = RenderHandler(self._wdmng, self._video, render)
            process = Process(target=renderer.render_file).start()
            self._renderers.append((renderer, process))
            self._queue.task_done()
        except Empty:
            return
