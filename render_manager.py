from render_handler import RenderHandler, RenderStatus

from queue import Empty
from multiprocessing import Process, Queue, Pool, Manager
    

class RenderManager():
    def __init__(self, wdmng, preprocess_handler):
        self._wdmng = wdmng
        self._preprocess_handler = preprocess_handler
        self.video, self.segments = "", []
        self._queue = Queue()
        self._renderers_queue = Queue()
        self._renderers = []
    
    @property
    def renderers(self):
        while not self._renderers_queue.empty():
            self._renderers.append(self._renderers_queue.get_nowait())
        return self._renderers
    
    @property
    def renderer_states(self):
        states = []
        for renderer in self.renderers:
            state = 0
            while not renderer[0].empty():
                state = renderer[0].get_nowait()
            states.append(state)
        return states


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
            render = self._queue.get()
            manager = Manager()
            queue = manager.Queue()
            renderer = RenderHandler(self._wdmng, self.video, render)
            process = Process(target=renderer.render_file, args=(queue,)).start()
            self._renderers_queue.put((queue, renderer))
        except Empty:
            return
