from render_handler import RenderHandler, RenderStatus

from queue import Empty
from multiprocessing import Process, Queue, Pool, Manager
    

class RenderManager():
    def __init__(self, wdmng, preprocess_handler):
        self._wdmng = wdmng
        self._preprocess_handler = preprocess_handler
        self.video, self.segments = "", []
        self._queue = Queue()
        self._manager = Manager()
        self.renderer_states = self._manager.list()
    
    def add_to_queue(self, render):
        self._queue.put(render)
    
    #def _join_finished(self):
    #    for renderer, process in self.renderers:
    #        if renderer.state[1] == RenderStatus.FINISH:
    #            # NOTE: arbitrary number, is it good?
    #            process.join(timeout=5)

    def _main_loop(self):
        self._render_next()
        #self._join_finished()
    
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
            renderer = RenderHandler(self._wdmng, self.video, render)
            process = Process(target=renderer.render_file, args=(state,)).start()
            self.renderer_states.append([state, render[1]])
        except Empty:
            return
