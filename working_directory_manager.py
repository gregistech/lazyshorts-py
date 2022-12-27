import tempfile
import uuid
from pathlib import Path
import os
import shutil

class WorkingDirectoryManager:
    def __init__(self, work_dir = False):
        self._work_dir = ""
        self.work_dir = work_dir
        self._is_work_dir_created = work_dir
        self._is_work_dir_set_by_user = work_dir
        self._registered = []
    
    def _ensure_work_dir(self):
        if not self._is_work_dir_created:
            if self._is_work_dir_set_by_user:
                Path(self._work_dir).mkdir(parents=True, exist_ok=True)
            else:
                self.work_dir = tempfile.mkdtemp() 
            self._is_work_dir_created = True
    @property
    def work_dir(self):
        self._ensure_work_dir()
        return self._work_dir
    @work_dir.setter
    def work_dir(self, work_dir):
        self._work_dir = work_dir + "/" if work_dir else False

    def __del__(self):
        self._cleanup_work_dir()

    def _delete_registered(self):
        for elem in self._registered:
            try:
                Path(elem).unlink(missing_ok=True)
            except IsADirectoryError:
                shutil.rmtree(elem)

    def _cleanup_work_dir(self):
        if self._is_work_dir_set_by_user:
            self._delete_registered()
        else:
            shutil.rmtree(self.work_dir)
    
    def _generate_name(self, name):
        return str(uuid.uuid4()) + name
    def _register_generated_name(self, name):
        return self.register_name(self._generate_name(name))
    def register_name(self, name):
        new_name = self.work_dir + name
        self._registered.append(new_name)
        return new_name

    def create_dir(self, directory):
        new_dir = self._register_generated_name(directory)
        Path(new_dir).mkdir(parents=True, exist_ok=True)
        return new_dir
    def create_file(self, file):
        return self._register_generated_name(file)
