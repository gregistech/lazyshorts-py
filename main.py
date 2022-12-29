from render_manager import RenderManager
from preprocess_handler import PreprocessHandler
from working_directory_manager import WorkingDirectoryManager
from transcriber import Transcriber
from ui import UI


if __name__ == '__main__':
    wdmng = WorkingDirectoryManager()
    transcriber = Transcriber()
    preprocess_handler = PreprocessHandler(wdmng, transcriber)

    rdmng = RenderManager(wdmng, preprocess_handler)

    UI(rdmng)

    # FIXME: will cause deadlock...
    mgmt_proc.join()
