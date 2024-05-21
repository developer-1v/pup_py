import subprocess, os, time, glob, tempfile, pkg_resources, site, difflib
from print_tricks import pt, C

class PipUniversalProjects:
    def __init__(self):
        self.cwd = os.getcwd()
        self.development_files_path = fr'{self.cwd}\DevelopmentFiles'
        self.init_file_path = fr'{self.cwd}\print_tricks\__init__.py'
        self.setup_file = f'{self.cwd}\\setup.py'
        self.function_steps_counter = [0]
