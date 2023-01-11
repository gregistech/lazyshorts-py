from .render_handler import RenderHandler, RenderStatus

from queue import Empty
from multiprocessing import Process, Queue, Pool, Manager
    

class RenderManager():
    def __init__(self, wdmng, preprocess_handler, end_text, end_time):
        self._wdmng = wdmng
        self._preprocess_handler = preprocess_handler
        self.video, self.segments = "", []
        self._queue = Queue()
        self._manager = Manager()
        self.renderer_states = self._manager.list()
        self._end_text, self._end_time = end_text, end_time
    
    def add_to_queue(self, render):
        self._queue.put(render)
    
    def _main_loop(self):
        self._render_next()
    
    def _start_execution(self, video, segments):
        self.video = video
        self.segments = segments
        while True:
            self._main_loop()

    def start(self, file):
        self.video, self.segments = self._preprocess_handler.process_video(file)
        Process(target=self._start_execution, args=(self.video, self.segments)).start()

    def _render_next(self):
        try:
            render = self._queue.get_nowait()
            state = self._manager.list()
            renderer = RenderHandler(self._wdmng, self.video, render, self._end_text, self._end_time)
            process = Process(target=renderer.render_file, args=(state,), daemon=True).start()
            self.renderer_states.append([state, render[1]])
        except Empty:
            return
