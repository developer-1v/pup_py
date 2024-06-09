
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
    - Integrate my conversion from setup.py to pyproject.toml


'''

import subprocess, os, sys, time, glob, tempfile, pkg_resources, site, difflib
import shutil, re
import site
from build.__main__ import build_package

from twine.commands.upload import upload as twine_upload
from twine.settings import Settings

from print_tricks import pt
from decorators import auto_decorate_methods
from setup_file_manager import SetupFileManager
from fix_and_optimize import fix_and_optimize
from pypi_verifier import PyPIVerifier
from ui_gui_manager import UiGuiManager

## TODO DELETE: Is this needed? TODO 
sys.path.append(os.path.dirname(__file__))


@auto_decorate_methods
class PipUniversalProjects:
    def __init__(self, 
        project_directory,
        destination_directory=None,
        package_name=None,
        distribution_subfolder='build_dist',
        pypi_structure_subfolder='pypi_system',
        pypi_build_subfolder='build_pypi',
        pypi_distribution_subfolder='dist_pypi',
        use_standard_build_directories=False,
        use_test_pypi=False,
        test_pypi_token_env_var='TEST_PYPI_TOKEN',
        pypi_token_env_var='PYPI_TOKEN',
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
        self.package_name = os.path.basename(project_directory) if package_name is None else package_name
        self.distribution_subfolder = distribution_subfolder
        self.pypi_structure_subfolder = pypi_structure_subfolder
        self.pypi_build_subfolder = pypi_build_subfolder
        self.pypi_distribution_subfolder = pypi_distribution_subfolder
        self.use_standard_build_directories = use_standard_build_directories
        self.use_test_pypi = use_test_pypi
        self.test_pypi_token_env_var = test_pypi_token_env_var
        self.pypi_token_env_var = pypi_token_env_var
        self.use_gui = use_gui
        
        self.ui_gui_manager = UiGuiManager(use_gui)
        self.wheel_path = None
        self.steps_counter = 0
        
        ## Execute
        self._execute_full_workflow()

    def _execute_full_workflow(self):
        self.user_options()
        self.create_directories()
        self.check_or_gen_requirements()
        self.setup_file_data()
        # pt.ex()
        self.verify_package_name_availability()
        self.fix_and_optimize_package()
        self.build_wheel()
        self.uninstall_existing_package()
        self.install_package_locally()
        self.test_installed_package() ## Test Local Wheel Package
        self.uninstall_local_package()
        self.upload_package_to_pypi()
        self.install_package_from_pypi()
        self.test_installed_package() ## Test Pypi intalled Package

    def user_options(self):
        
        self.user_options = {
            'fix_and_optimize': True, 
            'create_init_files': True, 
            'build_wheel': True, 
            'uninstall_existing_package': True, 
            'install_package_locally': True, 
            'test_installed_package': True, 
            'uninstall_local_package': True, 
            'upload_package_to_pypi': True, 
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

    def check_or_gen_requirements(self):
        ## Check if requirements.txt exists in either project_dir or build_dist_dir
        req_path_in_project = os.path.join(self.project_directory, 'requirements.txt')
        req_path_in_distribution_directory = os.path.join(self.distribution_directory, 'requirements.txt')
        pt(req_path_in_project, req_path_in_distribution_directory)
        
        if os.path.exists(req_path_in_project):
            if req_path_in_project != req_path_in_distribution_directory:
                shutil.copy(req_path_in_project, req_path_in_distribution_directory)
                pt.c('-- requirements.txt already exists, copying to distribution directory')
            return
        
        if os.path.exists(req_path_in_distribution_directory):
            pt.c('-- requirements.txt already exists.')
            return

        try:
            pt.c('-- Generating requirements.txt')
            
            if not os.path.exists(self.distribution_directory):
                os.makedirs(self.distribution_directory)
            pt(self.distribution_directory, req_path_in_distribution_directory)
            
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
        
        self.setup_file_manager = SetupFileManager(
            self.project_directory, 
            self.distribution_directory,
            self.package_name,
            
            
            )
        self.pyproject_data, self.pyproject_file_path = self.setup_file_manager.get_setup_file_data()

    def verify_package_name_availability(self):
        self.user_name = self.pyproject_data['username']
        
        verifier = PyPIVerifier(self.package_name)
        self.is_new_package, self.is_our_package, message = verifier.check_package_status(self.user_name)
        
        pt(message)
        
        if not self.is_our_package:
            new_package_name = self.user_manager.prompt_for_username()
            if new_package_name:
                self.package_name = new_package_name
                self.verify_package_name_availability()  ## Re-verify with new name

    def fix_and_optimize_package(self):
        
        fix_and_optimize(self.project_directory, self.distribution_directory, self.user_options)

    def build_wheel(self):
        import subprocess
        import os

        ## Debug Log the contents of the project directory
        # print("Contents of the project directory:")
        # for root, dirs, files in os.walk(self.project_directory):
        #     for file in files:
        #         print(os.path.join(root, file))

        pt(self.pyproject_file_path, self.project_directory, self.pypi_distribution_directory)
        
        
        print(f"\nBuilding package: '{self.package_name}' (will take a while...)")
        
        try:
            # Use the build library to build the project
            result = subprocess.run(
                [sys.executable, '-m', 'build', '--wheel', '--outdir', self.pypi_distribution_directory],
                cwd=self.project_directory,
                text=True,
                capture_output=True
            )
            if result.returncode != 0:
                pt.c("Build failed:", result.stdout, result.stderr)
                raise Exception(f"Build failed with errors: {result.stderr}")
            else:
                pt.c("Build succeeded:", result.stdout)
        except Exception as e:
            pt.e("Error during build:", str(e))
            raise

        ## Check for the wheel file in the output directory
        wheels = [f for f in os.listdir(self.pypi_distribution_directory) if f.endswith('.whl')]
        if wheels:
            self.wheel_path = os.path.join(self.pypi_distribution_directory, wheels[0])
            pt(self.wheel_path)
            return self.wheel_path
        else:
            raise FileNotFoundError("No wheel file created.")
    
    # def build_wheel(self):
    #     pt(self.pyproject_file_path, self.pypi_distribution_directory)
    #     # pt.ex()
    #     setup_args = ['python', self.pyproject_file_path, 'bdist_wheel', '--dist-dir', self.pypi_distribution_directory]
    #     # pt()
    #     subprocess.run(setup_args, cwd=self.project_directory, check=True)
    #     # pt()
    #     wheels = [f for f in os.listdir(self.pypi_distribution_directory) if f.endswith('.whl')]
    #     if wheels:
    #         self.wheel_path = os.path.join(self.pypi_distribution_directory, wheels[0])
    #         pt(self.wheel_path)
    #         return self.wheel_path
    #     else:
    #         raise FileNotFoundError("No wheel file created.")

    def uninstall_existing_package(self):
        # pt.ex()
        
        subprocess.run([sys.executable, '-m', 'pip', 'uninstall', self.package_name, '-y'], check=True)

    def install_package_locally(self):
        # Get the user base binary directory (where the scripts go)
        # user_script_dir = site.USER_BASE + os.sep + 'Scripts'
        
        # Add the user script directory to the PATH environment variable
        # os.environ['PATH'] += os.pathsep + user_script_dir
        # os.environ['PYTHONPATH'] = os.environ.get('PYTHONPATH', '') + os.pathsep + site.USER_SITE
        # pt(site.getsitepackages())
        # print(f"Added {user_script_dir} to PATH and PYTHONPATH")
        # sys.path.append(user_script_dir)
        
        # Explicitly add the directory where the package's scripts are installed
        # additional_script_dir = 'C:\\Users\\user\\AppData\\Roaming\\Python\\Python311\\Scripts'
        # os.environ['PATH'] += os.pathsep + additional_script_dir
        # print(f"Added {additional_script_dir} to PATH")
        
        pt(self.wheel_path)
        # pt.ex()
        subprocess.run(['pip', 'install', self.wheel_path, '--force-reinstall', '--user'], check=True)

    def test_installed_package(self):
        ## temp debug
        # user_site = site.getusersitepackages()
        # if user_site not in sys.path:
        #     sys.path.append(user_site)
        #     print(f"Added {user_site} to sys.path")
        # g = site.getsitepackages()
        # pt(g)
        
        ## Test 1: Check if the package is installed using `pip show`
        result_test_1 = subprocess.run([sys.executable, '-m', 'pip', 'show', self.package_name], capture_output=True, text=True)
        if result_test_1.returncode == 0 and self.package_name in result_test_1.stdout:
            print(f"Test 1 Success: The package '{self.package_name}' appears to be installed.")
        else:
            print(f"Test 1 Failure: The package '{self.package_name}' is not installed or not found by pip.")
            sys.exit(1)
        
        ## Test 2: Attempt to import the package to verify it's accessible to Python
        try:
            __import__(self.package_name)
            print(f"Test 2 Success: The package '{self.package_name}' was successfully imported.")
        except ImportError as e:
            print(f"Test 2 Failure: Could not import the package '{self.package_name}'. Error: {e}")
            sys.exit(1)
        
        ## Test 3: Execute a small script to ensure the package's basic functionality
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp:
            temp.write(
                f'import {self.package_name}\n'
                f'print("Test 3 Success: The package \'{self.package_name}\' is successfully being executed in a test script.")\n'.encode('utf-8')
            )
            temp_file_name = temp.name
        try:
            result = subprocess.run([sys.executable, temp_file_name], capture_output=True, text=True)
            print(result.stdout)
            if result.returncode != 0:
                print(f"Test 3 Failure: Error running test script for '{self.package_name}': {result.stderr}")
                sys.exit(1)
        finally:
            os.remove(temp_file_name)
            
        print(f"Details for installed package '{self.package_name}':\n{result_test_1.stdout}")

    def uninstall_local_package(self):
        subprocess.run([sys.executable, '-m', 'pip', 'uninstall', self.package_name, '-y'], check=True)

    def upload_package_to_pypi(self):
        if self.use_test_pypi:
            repository_url = 'https://test.pypi.org/legacy/'
            token = os.getenv(self.test_pypi_token_env_var)
        else:
            repository_url = 'https://upload.pypi.org/legacy/'
            token = os.getenv(self.pypi_token_env_var)

        ## Check if the token is available
        if not token:
            error_message = f"""
Error: {'Test ' if self.use_test_pypi else ''}PyPI token not found. Please set the {'TEST_PYPI_TOKEN' if self.use_test_pypi else 'PYPI_TOKEN'} environment variable.

To obtain and set a PyPI token:
1. Visit the PyPI token management page: https://pypi.org/help/#apitoken
2. Follow the instructions to generate a new token.
3. Set the token as an environment variable on your system:
    - Windows: https://docs.microsoft.com/en-us/windows/deployment/usmt/usmt-recognized-environment-variables
    - macOS/Linux: https://developer.apple.com/documentation/xcode/defining-environment-variables-for-mac-apps

For a visual guide on generating and setting PyPI tokens, watch this YouTube tutorial: https://youtu.be/WGsMydFFPMk?t=104 (Should start at 1:44 and last for 2 minutes to 3:45)
            """
            print(error_message)
            sys.exit(1)
        
        pt.c(f'Uploading Package to {"Test PyPI" if self.use_test_pypi else "PyPI"} using token authentication')

        ## Setup Twine settings with the token
        settings = Settings(
            repository_url=repository_url,
            username="__token__",
            password=token,
            non_interactive=True,
            verbose=True,
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
    # subprocess.run([sys.executable, clean_and_create_new_projects_path], check=True)
    # pt.ex()
    
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
            # test_pypi_token_env_var='NON-EXISTANT_PYPI_TOKEN_FOR_TESTING',
            )

if __name__ == '__main__':
    test()