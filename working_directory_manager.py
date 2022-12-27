import shutil
import tempfile
import uuid
from pathlib import Path
import os

class WorkingDirectoryManager:
    def __init__(self, work_dir = False):
        self._work_dir = ""
        self.work_dir = work_dir
        self._is_work_dir_created = work_dir
        self._is_work_dir_set_by_user = work_dir
        self._registered_files = []

    @property
    def work_dir(self):
        if not self._is_work_dir_created:
            if self._is_work_dir_set_by_user:
                Path(self._work_dir).mkdir(parents=True, exist_ok=True)
            else:
                self.work_dir = tempfile.mkdtemp() 
        return self._work_dir
    @work_dir.setter
    def work_dir(self, work_dir):
        self._work_dir = work_dir + "/"

    def __del__(self):
        self._cleanup_work_dir()

    def _delete_registered_files(self):
        for file in self._registered_files:
            os.remove(file)

    def _cleanup_work_dir(self):
        if self._is_work_dir_set_by_user:
            self._delete_registered_files()
        else:
            shutil.rmtree(self.work_dir)

    def create_file(self, file):
        new_file = self.work_dir + str(uuid.uuid4()) + file
        self._registered_files.append(new_file)
        return new_file
