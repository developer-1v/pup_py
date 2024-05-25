
'''PUP (Pip Universal Projects) - An automated one-click solution for pip 
    package management:
    PUP takes a project_dir, builds a pip package, uploads it to PyPI, and 
    manages its installation.
    
    Steps included:
    - Initialize setup.py (Generate and/or read data).
    - Build the wheel file
    - Uninstall any previous version of the package
    - Install the newly created wheel locally
    - Test the installed wheel
    - Uninstall the local wheel
    - Upload the wheel to PyPI
    - Install the package from PyPI
'''

import subprocess, os, time, glob, tempfile, pkg_resources, site, difflib
from print_tricks import pt, C

import subprocess
import os
import shutil
import sys
from setuptools import setup
from twine.commands.upload import upload as twine_upload
import textwrap


import os
import textwrap
import re

import os

class SetupFileManager:
    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.setup_file_data = self.get_setup_file_data()

    def get_setup_file_data(self):
        setup_py_path = os.path.join(self.project_dir, 'setup.py')
        main_py_path = os.path.join(self.project_dir, 'main.py')
        template_path = os.path.join(os.path.dirname(__file__), 'setup_template.py')

        # Try to read setup.py from the project directory
        if os.path.exists(setup_py_path):
            return self.parse_setup_file(setup_py_path)

        # If setup.py is not found, try to read main.py
        elif os.path.exists(main_py_path):
            return self.parse_setup_file(main_py_path)

        # If neither setup.py nor main.py are found, use the setup_template.py
        else:
            return self.parse_setup_file(template_path)

    def parse_setup_file(self, file_path):
        with open(file_path, 'r') as file:
            content = file.read()

        # Extract package name and version
        package_name = self.extract_value(content, 'name=')
        version = self.extract_value(content, 'version=')

        return {'package_name': package_name, 'version': version}

    def extract_value(self, content, key):
        # Find the line containing the key and extract the value
        start = content.find(key) + len(key)
        if start != -1:
            end = content.find(',', start)
            if end == -1:
                end = len(content)
            value = content[start:end].strip().strip("'\"")
            return value
        return None

class PipUniversalProjects:
    def __init__(self, project_dir, destination_dir, package_name=None):
        self.project_dir = project_dir
        self.destination_dir = destination_dir
        self.main_folder = os.path.join(destination_dir, 'build_dist')
        self.package_name = os.path.basename(project_dir) if package_name is None else package_name
        self.dist_dir = os.path.join(self.main_folder, 'dist')
        self.build_dir = os.path.join(self.main_folder, 'build')
        os.makedirs(self.dist_dir, exist_ok=True)
        os.makedirs(self.build_dir, exist_ok=True)
        self.wheel_path = None
        self.steps_counter = 0
        
        self.execute_full_workflow

    def execute_full_workflow(self):
        self.setup_file_data()
        self.build_wheel()
        self.uninstall_package()
        self.install_wheel_locally()
        self.test_installed_package()
        self.uninstall_local_wheel()
        self.upload_wheel_to_pypi()
        self.install_package_from_pypi()

    def setup_file_data(self):
        self.steps_counter += 1
        pt.c(f'------------------------{self.steps_counter} Initializing Setup File Data------------------------')
        
        self.setup_data = SetupFileManager(self.project_dir)

    def build_wheel(self):
        self.steps_counter += 1
        pt.c(f'------------------------{self.steps_counter} Building Wheel------------------------')
        
        setup_args = ['python', 'setup.py', 'bdist_wheel', '--dist-dir', self.dist_dir]
        subprocess.run(setup_args, cwd=self.project_dir, check=True)
        wheels = [f for f in os.listdir(self.dist_dir) if f.endswith('.whl')]
        if wheels:
            return os.path.join(self.dist_dir, wheels[0])
        else:
            raise FileNotFoundError("No wheel file created.")

    def uninstall_package(self):
        self.steps_counter += 1
        pt.c(f'------------------------{self.steps_counter} Uninstalling Existing Package (if any)------------------------')
        
        subprocess.run([sys.executable, '-m', 'pip', 'uninstall', self.package_name, '-y'], check=True)

    def install_wheel_locally(self):
        self.steps_counter += 1
        pt.c(f'------------------------{self.steps_counter} Installing Package Locally------------------------')
        subprocess.run([sys.executable, '-m', 'pip', 'install', self.wheel_path, '--force-reinstall'], check=True)

    def test_installed_package(self):
        self.steps_counter += 1
        pt.c(f'------------------------{self.steps_counter} Testing Locally Installed Package------------------------')
        # Implement specific tests for your package
        print("Testing installed package...")

    def uninstall_local_wheel(self):
        self.steps_counter += 1
        pt.c(f'------------------------{self.steps_counter} Uninstalling Local Package------------------------')
        subprocess.run([sys.executable, '-m', 'pip', 'uninstall', self.package_name, '-y'], check=True)

    def upload_wheel_to_pypi(self):
        self.steps_counter += 1
        pt.c(f'------------------------{self.steps_counter} Uploading Package to PyPI------------------------')
        twine_upload(['upload', self.wheel_path])

    def install_package_from_pypi(self):
        self.steps_counter += 1
        pt.c(f'------------------------{self.steps_counter} Installing Package from PyPI------------------------')
        subprocess.run([sys.executable, '-m', 'pip', 'install', self.package_name], check=True)

def main():
    pup = PipUniversalProjects(
        project_dir=r'C:\.PythonProjects\smak', 
        destination_dir=r'C:\.PythonProjects\smak\build_dist',
        )




if __name__ == '__main__':
    main()
