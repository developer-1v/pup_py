
'''PUP (Pip Universal Projects) - An automated one-click solution for pip 
    package management:
    PUP takes a project_directory builds a pip package, uploads it to PyPI, and 
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
import shutil, re
import site
from twine.commands.upload import upload as twine_upload
from twine.settings import Settings

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
    def __init__(self, 
            project_directory, 
            destination_directory=None,
            distribution_subfolder='build_dist',
            pypi_structure_subfolder='pypi_system',
            pypi_build_subfolder='build_pypi',
            pypi_distribution_subfolder='dist_pypi',
            use_standard_build_directories=False,
            package_name=None, 
            use_test_pypi=False,
            use_gui=False,
            ):
        
        ## Check for Valid Project:
        if not os.path.exists(project_directory):
            pt.c(' -- You must pass a legitimate project directory to try to process this!!!')
            pt.c(' -- Error: message for production:')
            raise FileNotFoundError(f'Project directory {project_directory} does not exist.')
        
        ## Args
        self.project_directory = project_directory
        self.destination_directory = project_directory if destination_directory is None else destination_directory
        self.distribution_subfolder = distribution_subfolder
        self.pypi_structure_subfolder = pypi_structure_subfolder
        self.pypi_build_subfolder = pypi_build_subfolder
        self.pypi_distribution_subfolder = pypi_distribution_subfolder
        self.use_standard_build_directories = use_standard_build_directories
        self.package_name = os.path.basename(project_directory) if package_name is None else package_name
        self.use_test_pypi = use_test_pypi
        self.use_gui = use_gui
        
        self.ui_gui_manager = UiGuiManager(use_gui)
        self.wheel_path = None
        self.steps_counter = 0
        
        ## Execute
        self._execute_full_workflow()

    def _execute_full_workflow(self):
        self.user_options()
        self.create_directories()
        self.check_gen_requirements()
        # pt.ex()
        self.setup_file_data()
        self.verify_package_name_availability()
        self.fix_and_optimize_package()
        self.build_wheel()
        self.uninstall_package()
        self.install_wheel_locally()
        # pt.ex()
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

    def create_directories(self):
        
        ## For "Traditional" building locations/directories
        if self.use_standard_build_directories:
            self.distribution_subfolder = ''
            self.pypi_structure_subfolder=''
            self.pypi_build_subfolder='build'
            self.pypi_distribution_subfolder='dist'
            
            pt(
                self.distribution_subfolder, 
                self.pypi_structure_subfolder, 
                self.pypi_build_subfolder, 
                self.pypi_distribution_subfolder
            )
            
        ## pup_py recommmended Subdirectories for project
        self.distribution_directory = os.path.join(self.destination_directory, self.distribution_subfolder)
        self.pypi_structure_directory = os.path.join(self.distribution_directory, self.pypi_structure_subfolder)
        self.pypi_build_directory = os.path.join(self.pypi_structure_directory, self.pypi_build_subfolder)
        self.pypi_distribution_directory = os.path.join(self.pypi_structure_directory, self.pypi_distribution_subfolder)
        os.makedirs(self.pypi_distribution_directory, exist_ok=True)
        os.makedirs(self.pypi_build_directory, exist_ok=True)
        
        ## TEMP: Creation of exe directories for organizational testing
        ## These would normally only be created in the Persist App for creating exe's. 
        ## But is here for testing compatibility between the two systems. 
        self.exe_structure_directory = os.path.join(self.distribution_directory, 'exe_system')
        self.exe_distribution_directory = os.path.join(self.exe_structure_directory, 'dist_exe')
        self.exe_build_directory = os.path.join(self.exe_structure_directory, 'build_exe')
        os.makedirs(self.exe_distribution_directory, exist_ok=True)
        os.makedirs(self.exe_build_directory, exist_ok=True)

    def check_gen_requirements(self):
        # Check if requirements.txt exists in either project_dir or build_dist_dir
        req_path_in_project = os.path.join(self.project_directory, 'requirements.txt')
        req_path_in_distribution_directory = os.path.join(self.distribution_directory, 'requirements.txt')
        pt(req_path_in_project, req_path_in_distribution_directory)
        if os.path.exists(req_path_in_project):
            shutil.copy(req_path_in_project, req_path_in_distribution_directory)
            pt.c('-- requirements.txt already exists, copying to build_dist_dir')
            return
        
        if os.path.exists(req_path_in_distribution_directory):
            pt.c('-- requirements.txt already exists.')
            return

        try:
            pt.c('-- Generating requirements.txt')
            # Ensure the directory exists
            if not os.path.exists(self.distribution_directory):
                os.makedirs(self.distribution_directory)
            pt(self.distribution_directory, req_path_in_distribution_directory)
            # pt.ex()
            ignore_dirs = 'dist,build,venv,pycache'  ## NOTE: No spaces after commas!!!
            subprocess.run([
                    'pipreqs', 
                    self.distribution_directory, 
                    '--force',  
                    f'--ignore={ignore_dirs}',
                    '--savepath', req_path_in_distribution_directory
                    ],
                check=True)
            pt.c('-- Finished Creating requirements.txt in build_dist_dir')
        except Exception as e:
                pt.e()
                pt.ex(e)

    def setup_file_data(self):
        
        self.setup_file_manager = SetupFileManager(self.project_directory, self.distribution_directory)
        self.setup_file_data, self.setup_file_path = self.setup_file_manager.get_setup_file_data()

    def verify_package_name_availability(self):
        
        verifier = PyPIVerifier(self.package_name)
        self.is_new_package, self.is_our_package, message = verifier.check_package_status("your_username")
        
        pt(message)
        
        if not self.is_our_package:
            new_package_name = self.user_manager.prompt_for_username()
            if new_package_name:
                self.package_name = new_package_name
                self.verify_package_name_availability()  ## Re-verify with new name

    def fix_and_optimize_package(self):
        
        fix_and_optimize(self.project_directory, self.distribution_directory, self.user_options)

    def build_wheel(self):
        
        pt(self.setup_file_path, self.distribution_directory)
        # pt.ex()
        setup_args = ['python', self.setup_file_path, 'bdist_wheel', '--dist-dir', self.distribution_directory]
        # pt()
        subprocess.run(setup_args, cwd=self.project_directory, check=True)
        # pt()
        wheels = [f for f in os.listdir(self.distribution_directory) if f.endswith('.whl')]
        if wheels:
            self.wheel_path = os.path.join(self.distribution_directory, wheels[0])
            return self.wheel_path
        else:
            raise FileNotFoundError("No wheel file created.")

    def uninstall_package(self):
        
        subprocess.run([sys.executable, '-m', 'pip', 'uninstall', self.package_name, '-y'], check=True)



    def install_wheel_locally(self):
        # Get the user base binary directory (where the scripts go)
        user_script_dir = site.USER_BASE + os.sep + 'Scripts'
        
        # Add the user script directory to the PATH environment variable
        os.environ['PATH'] += os.pathsep + user_script_dir
        pt(user_script_dir, os.pathsep + user_script_dir)
        print(f"Added {user_script_dir} to PATH")
        sys.path.append(user_script_dir)
        # pt.ex()
        # pt.ex()
        # Now run pip install with the --user option
        subprocess.run([sys.executable, '-m', 'pip', 'install', self.wheel_path, '--force-reinstall', '--user'], check=True)


    def test_installed_package(self):
        print("Testing installed package...")

    def uninstall_local_wheel(self):
        subprocess.run([sys.executable, '-m', 'pip', 'uninstall', self.package_name, '-y'], check=True)

    def upload_wheel_to_pypi(self):
        # Determine the correct repository URL and token based on whether you're using Test PyPI or PyPI
        if self.use_test_pypi:
            repository_url = 'https://test.pypi.org/legacy/'
            token = os.getenv('TEST_PYPI_TOKEN')
        else:
            repository_url = 'https://upload.pypi.org/legacy/'
            token = os.getenv('PYPI_TOKEN')

        # Check if the token is available
        if not token:
            raise Exception(f"{'Test ' if self.use_test_pypi else ''}PyPI token not found. Please set the {'TEST_PYPI_TOKEN' if self.use_test_pypi else 'PYPI_TOKEN'} environment variable.")

        pt.c(f'Uploading Package to {"Test PyPI" if self.use_test_pypi else "PyPI"} using token authentication')

        # Setup Twine settings with the token
        settings = Settings(
            repository_url=repository_url,
            username="__token__",
            password=token,
            non_interactive=True,
            # verbose=True,
        )
        dists = [self.wheel_path]
        twine_upload(settings, dists)

    def install_package_from_pypi(self):
        pypi_type = 'Test PyPI' if self.use_test_pypi else 'PyPI'
        pt.c(f'Installing Package from {pypi_type}')
        index_url = 'https://test.pypi.org/simple/' if self.use_test_pypi else 'https://pypi.org/simple'
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--index-url', index_url, self.package_name], check=True)



# def main(project_directory, destination_directory=None):
#     ...
#     pup = PipUniversalProjects(
#         project_directory=project_directory,
#         destination_directory=destination_directory,
#     )

def test():
    base_path = r'C:\.PythonProjects\SavedTests\_test_projects_for_building_packages'
    main_projects_path = os.path.join(
        base_path, 'projects')
    clean_and_create_new_projects_path = os.path.join(
        base_path, 'clean_and_create_new_projects.py')
    
    ## Clean out old projects and create new ones
    subprocess.run([sys.executable, clean_and_create_new_projects_path], check=True)
    
    ## Dynamically get names of all test projects that start with a capital letter and underscore:
    project_dirs = [name for name in os.listdir(main_projects_path)
                    if os.path.isdir(os.path.join(main_projects_path, name)) and re.match(r'[A-Z]_', name)]

    ## TODO DELETE: temporary testing of individual projects
    project_dirs = ['A_with_nothing',
                    # 'B_with_pyproject_toml',
                    # 'C_with_setup_py',
                    # 'D_with_requirements',
                    # 'E_with_existing_init_files',
                    ]

    for project_dir in project_dirs:    
        PipUniversalProjects(
            project_directory=os.path.join(main_projects_path, project_dir),
            use_standard_build_directories=True,
            use_test_pypi=True,
            )
        
if __name__ == '__main__':
    test()