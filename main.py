
'''PUP (Pip Universal Projects) - An automated one-click solution for pip 
    package management:
    PUP takes a project_dir, builds a pip package, uploads it to PyPI, and 
    manages its installation.
    
    Steps included:
    - Get user options (optional)
    - Initialize setup.py (Generate and/or read data).
    - Verify availability of package name
    - Fix and optimize package (optional)
    - Build the wheel file
    - Uninstall any previous version of the package
    - Install the newly created wheel locally
    - Test the installed wheel
    - Uninstall the local wheel
    - Upload the wheel to PyPI or Test Pypi
    - Install the package from PyPI or Test Pypi
    
    
    TODO:
    - replace setup.py with pyproject.toml and setuptools with "build" library. 
    - if they have a setup.py in their project, then convert it to pyproject.toml
    and place in our build_dist directory.
    
'''

import subprocess, os, sys, time, glob, tempfile, pkg_resources, site, difflib
import shutil

from setuptools import setup
from twine.commands.upload import upload as twine_upload

from print_tricks import pt
from decorators import auto_decorate_methods
from setup_file_manager import SetupFileManager
from fix_and_optimize import fix_and_optimize
from pypi_verifier import PyPIVerifier
from ui_gui_manager import UiGuiManager

## TODO DELETE: Is this needed? 
sys.path.append(os.path.dirname(__file__))


@auto_decorate_methods
class PipUniversalProjects:
    def __init__(self, project_dir, destination_dir=None, package_name=None, use_gui=False):
        self.project_dir = project_dir
        self.destination_dir = project_dir if destination_dir is None else destination_dir
        self.package_name = os.path.basename(project_dir) if package_name is None else package_name
        self.use_gui = use_gui
        
        ## subdirectories for project
        self.build_dist_dir = os.path.join(self.destination_dir, 'build_dist')
        self.pypi_system_dir = os.path.join(self.build_dist_dir, 'pypi_system')
        self.dist_dir = os.path.join(self.pypi_system_dir, 'dist_pypi')
        self.build_dir = os.path.join(self.pypi_system_dir, 'build_pypi')
        os.makedirs(self.dist_dir, exist_ok=True)
        os.makedirs(self.build_dir, exist_ok=True)
        
        ## TEMP: Creation of exe directories for organizational testing
        self.exe_system_dir = os.path.join(self.build_dist_dir, 'exe_system')
        self.exe_dist_dir = os.path.join(self.exe_system_dir, 'dist_exe')
        self.exe_build_dir = os.path.join(self.exe_system_dir, 'build_exe')
        os.makedirs(self.exe_dist_dir, exist_ok=True)
        os.makedirs(self.exe_build_dir, exist_ok=True)
        
        ## Other args:
        self.ui_gui_manager = UiGuiManager(use_gui)
        args = sys.argv
        self.wheel_path = None
        self.steps_counter = 0
        
        ## EXECUTE!
        self._execute_full_workflow()

    def _execute_full_workflow(self):
        self.user_options()
        self.check_gen_requirements()
        self.setup_file_data()
        self.verify_package_name()
        self.fix_and_optimize_package()
        self.build_wheel()
        self.uninstall_package()
        self.install_wheel_locally()
        pt.ex()
        self.test_installed_package()
        self.uninstall_local_wheel()
        self.upload_wheel_to_pypi()
        self.install_package_from_pypi()

    def user_options(self):
        
        self.user_options = {
            'fix_and_optimize': True, 
            'create_init_files': True, 
            'build_wheel': True, 
            'uninstall_package': True, 
            'install_wheel_locally': True, 
            'test_installed_package': True, 
            'uninstall_local_wheel': True, 
            'upload_wheel_to_pypi': True, 
            'install_package_from_pypi': True,
            'excluded_folders': [''],
            }

    def check_gen_requirements(self):
        # Check if requirements.txt exists in either project_dir or build_dist_dir
        requirements_path_project = os.path.join(self.project_dir, 'requirements.txt')
        requirements_path_build = os.path.join(self.build_dist_dir, 'requirements.txt')

        if os.path.exists(requirements_path_project):
            shutil.copy(requirements_path_project, requirements_path_build)
            pt.c('-- requirements.txt already exists, copying to build_dist_dir')
            return
        
        if os.path.exists(requirements_path_build):
            pt.c('-- requirements.txt already exists.')
            return

        try:
            pt.c('-- Generating requirements.txt')
            # Ensure the directory exists
            if not os.path.exists(self.build_dist_dir):
                os.makedirs(self.build_dist_dir)
            pt(self.build_dist_dir)

            ignore_dirs = 'dist,build,venv,pycache'  # No spaces after commas
            subprocess.run([
                    'pipreqs', 
                    self.build_dist_dir, 
                    '--force',  
                    f'--ignore={ignore_dirs}',
                    '--savepath', requirements_path_build
                    ],
                check=True)
            pt.c('-- Finished Creating requirements.txt in build_dist_dir')
        except Exception as e:
                pt.e()
                pt.ex(e)

    def setup_file_data(self):
        
        self.setup_file_manager = SetupFileManager(self.project_dir, self.build_dist_dir)
        self.setup_file_data, self.setup_file_path = self.setup_file_manager.get_setup_file_data()

    def verify_package_name(self):
        
        verifier = PyPIVerifier(self.package_name)
        self.is_new_package, self.is_our_package, message = verifier.check_package_status("your_username")
        
        pt(message)
        
        if not self.is_our_package:
            new_package_name = self.user_manager.prompt_for_username()
            if new_package_name:
                self.package_name = new_package_name
                self.verify_package_name()  ## Re-verify with new name

    def fix_and_optimize_package(self):
        
        fix_and_optimize(self.project_dir, self.user_options)

    def build_wheel(self):
        
        pt(self.setup_file_path, self.dist_dir)
        # pt.ex()
        setup_args = ['python', self.setup_file_path, 'bdist_wheel', '--dist-dir', self.dist_dir]
        # pt()
        subprocess.run(setup_args, cwd=self.project_dir, check=True)
        # pt()
        wheels = [f for f in os.listdir(self.dist_dir) if f.endswith('.whl')]
        if wheels:
            self.wheel_path = os.path.join(self.dist_dir, wheels[0])
            return self.wheel_path
        else:
            raise FileNotFoundError("No wheel file created.")

    def uninstall_package(self):
        
        subprocess.run([sys.executable, '-m', 'pip', 'uninstall', self.package_name, '-y'], check=True)

    def install_wheel_locally(self):
        subprocess.run([sys.executable, '-m', 'pip', 'install', self.wheel_path, '--force-reinstall'], check=True)

    def test_installed_package(self):
        print("Testing installed package...")

    def uninstall_local_wheel(self):
        subprocess.run([sys.executable, '-m', 'pip', 'uninstall', self.package_name, '-y'], check=True)

    def upload_wheel_to_pypi(self, test_pypi=False):
        repository_url = 'https://test.pypi.org/legacy/' if test_pypi else 'https://upload.pypi.org/legacy/'
        pt.c(f'Uploading Package to {"Test PyPI" if test_pypi else "PyPI"}')
        twine_upload(['upload', '--repository-url', repository_url, self.wheel_path])

    def install_package_from_pypi(self, test=False):
        pypi_name = 'Test PyPI' if test else 'PyPI'
        pt.c(f'Installing Package from {pypi_name}')
        index_url = 'https://test.pypi.org/simple/' if test else 'https://pypi.org/simple'
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--index-url', index_url, self.package_name], check=True)


def main(project_dir, destination_dir=None):
    ...
    pup = PipUniversalProjects(
        project_dir=project_dir, 
        destination_dir=destination_dir,
        )


if __name__ == '__main__':
    project_dirs = [
        "A_with_setup_py",
        "B_with_main",
        "C_with_nothing",
        "D_with_requirements",
        "E_with_existing_init_files",
        ]

    for project_dir in project_dirs:    
        main(
            project_dir=os.path.join(
                r'C:\.PythonProjects\SavedTests\test_projects_for_building_packages', project_dir),
        )