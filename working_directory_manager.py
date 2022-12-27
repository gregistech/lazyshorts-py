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
        self._registered = []

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

    def _delete_registered(self):
        for file in self._registered:
            Path(file).unlink(missing_ok=True)

    def _cleanup_work_dir(self):
        if self._is_work_dir_set_by_user:
            self._delete_registered()
        else:
            Path(self.work_dir).unlink(missing_ok=True)
    
    def _generate_name(self, name):
        return self.work_dir + str(uuid.uuid4()) + name
    def _register_name(self, name):
        new_name = self._generate_name(name)
        self._registered.append(new_name)
        return new_name


    def create_dir(self, directory):
        new_dir = self._register_name(directory)
        Path(new_dir).mkdir(parents=True, exist_ok=True)
        return new_dir
    def create_file(self, file):
        return self._register_name(file)
