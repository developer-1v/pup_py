
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
    
    
    
'''

import subprocess, os, sys, time, glob, tempfile, pkg_resources, site, difflib

from setuptools import setup
from twine.commands.upload import upload as twine_upload

from print_tricks import pt
from setup_file_manager import SetupFileManager
from fix_and_optimize import fix_and_optimize
from pypi_verifier import PyPIVerifier

## TODO DELETE: Is this needed? 
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
        
        ## EXECUTE!
        self.execute_full_workflow()

    def execute_full_workflow(self):
        self.user_options()
        self.setup_file_data()
        self.verify_package_name()
        self.fix_and_optimize_package()
        pt.ex()
        self.build_wheel()
        self.uninstall_package()
        self.install_wheel_locally()
        self.test_installed_package()
        self.uninstall_local_wheel()
        self.upload_wheel_to_pypi()
        self.install_package_from_pypi()
    
    def user_options(self):
        self.steps_counter += 1
        pt.c(f'\n------------------------{self.steps_counter} User Options------------------------')
        
        self.user_options = {
            'fix_and_optimize': True, 
            'create_init_files': True, 
            'build_wheel': True, 
            'uninstall_package': True, 
            'install_wheel_locally': True, 
            'test_installed_package': True, 
            'uninstall_local_wheel': True, 
            'upload_wheel_to_pypi': True, 
            'install_package_from_pypi': True}
        
    
    def setup_file_data(self):
        self.steps_counter += 1
        pt.c(f'\n------------------------{self.steps_counter} Initializing Setup File Data------------------------')
        
        self.setup_file_manager = SetupFileManager(self.project_dir, self.build_dist_dir)
        self.setup_file_data, self.setup_file_path = self.setup_file_manager.get_setup_file_data()

    def verify_package_name(self):
        self.steps_counter += 1
        pt.c(f'\n------------------------{self.steps_counter} Verifying Package Name------------------------')
        
        verifier = PyPIVerifier(self.package_name)
        pt(verifier.is_package_available())
        pt(verifier.verify_package_owner("your_username"))
        pt.ex()

    def fix_and_optimize_package(self):
        self.steps_counter += 1
        pt.c(f'\n------------------------{self.steps_counter} Fixing and Optimizing Package------------------------')
        
        fix_and_optimize(self.user_options, self.project_dir)

    def build_wheel(self):
        self.steps_counter += 1
        pt.c(f'\n------------------------{self.steps_counter} Building Wheel------------------------')
        
        setup_args = ['python', self.setup_file_path, 'bdist_wheel', '--dist-dir', self.dist_dir]
        # pt()
        subprocess.run(setup_args, cwd=self.project_dir, check=True)
        # pt()
        wheels = [f for f in os.listdir(self.dist_dir) if f.endswith('.whl')]
        if wheels:
            return os.path.join(self.dist_dir, wheels[0])
        else:
            raise FileNotFoundError("No wheel file created.")

    def uninstall_package(self):
        self.steps_counter += 1
        pt.c(f'\n------------------------{self.steps_counter} Uninstalling Existing Package (if any)------------------------')
        
        subprocess.run([sys.executable, '-m', 'pip', 'uninstall', self.package_name, '-y'], check=True)

    def install_wheel_locally(self):
        self.steps_counter += 1
        pt.c(f'\n------------------------{self.steps_counter} Installing Package Locally------------------------')
        subprocess.run([sys.executable, '-m', 'pip', 'install', self.wheel_path, '--force-reinstall'], check=True)

    def test_installed_package(self):
        self.steps_counter += 1
        pt.c(f'\n------------------------{self.steps_counter} Testing Locally Installed Package------------------------')
        # Implement specific tests for your package
        print("Testing installed package...")

    def uninstall_local_wheel(self):
        self.steps_counter += 1
        pt.c(f'\n------------------------{self.steps_counter} Uninstalling Local Package------------------------')
        subprocess.run([sys.executable, '-m', 'pip', 'uninstall', self.package_name, '-y'], check=True)

    def upload_wheel_to_pypi(self, test_pypi=False):
        self.steps_counter += 1
        repository_url = 'https://test.pypi.org/legacy/' if test_pypi else 'https://upload.pypi.org/legacy/'
        pt.c(f'\n------------------------{self.steps_counter} Uploading Package to {"Test PyPI" if test_pypi else "PyPI"}------------------------')
        twine_upload(['upload', '--repository-url', repository_url, self.wheel_path])

    def install_package_from_pypi(self, test=False):
        self.steps_counter += 1
        pypi_name = 'Test PyPI' if test else 'PyPI'
        pt.c(f'\n------------------------{self.steps_counter} Installing Package from {pypi_name}------------------------')
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