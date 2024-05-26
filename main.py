
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

import subprocess, os, sys, time, glob, tempfile, pkg_resources, site, difflib

from setuptools import setup
from twine.commands.upload import upload as twine_upload

from print_tricks import pt
from setup_file_manager import SetupFileManager

sys.path.append(os.path.dirname(__file__))



class PipUniversalProjects:
    def __init__(self, project_dir, destination_dir=None, package_name=None):
        self.project_dir = project_dir

        self.destination_dir = project_dir if destination_dir is None else destination_dir
        self.build_dist_dir = os.path.join(self.destination_dir, 'build_dist')
        self.pypi_system_dir = os.path.join(self.build_dist_dir, 'pypi_system')
        
        ## Subdirectories for wheel
        self.dist_dir = os.path.join(self.pypi_system_dir, 'dist_pypi')
        self.build_dir = os.path.join(self.pypi_system_dir, 'build_pypi')
        os.makedirs(self.dist_dir, exist_ok=True)
        os.makedirs(self.build_dir, exist_ok=True)
        
        args = sys.argv
        self.package_name = os.path.basename(project_dir) if package_name is None else package_name
        self.wheel_path = None
        self.steps_counter = 0
        
        ## TEMP: Creation of exe directories for organizational testing
        self.exe_system_dir = os.path.join(self.build_dist_dir, 'exe_system')
        self.exe_dist_dir = os.path.join(self.exe_system_dir, 'dist_exe')
        self.exe_build_dir = os.path.join(self.exe_system_dir, 'build_exe')
        os.makedirs(self.exe_dist_dir, exist_ok=True)
        os.makedirs(self.exe_build_dir, exist_ok=True)
        
        self.setup_file_path = os.path.join(self.build_dist_dir, 'setup.py')
        
        ## EXECUTE!
        self.execute_full_workflow()

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
        
        self.setup_data = SetupFileManager(self.project_dir, self.build_dist_dir)

    def build_wheel(self):
        self.steps_counter += 1
        pt.c(f'------------------------{self.steps_counter} Building Wheel------------------------')
        
        setup_args = ['python', self.setup_file_path, 'bdist_wheel', '--dist-dir', self.dist_dir]
        pt()
        subprocess.run(setup_args, cwd=self.project_dir, check=True)
        pt()
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
    ...
    # pup = PipUniversalProjects(
    #     project_dir=r'C:\.PythonProjects\smak', 
    #     destination_dir=r'C:\.PythonProjects\smak\build_dist',
    #     )




if __name__ == '__main__':
    # main()
    pup = PipUniversalProjects(
    project_dir=r'C:\.PythonProjects\SavedTests\test_package_for_builds', 
    # destination_dir=r'C:\.PythonProjects\test_output',
    )
