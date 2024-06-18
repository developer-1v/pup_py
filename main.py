
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
    
    - Allow the project_directory to be any url, not just a git repository or 
    local directory. Note: I'd get rid of "git" and the cloning. 
        - Possible approach 1:
            import subprocess
            url = "https://data.chc.ucsb.edu/products/EWX/data/forecasts/CHIRPS-GEFS_precip_v12/daily_16day/2016/01/02"
            destination = "/path/to/download/directory"
            subprocess.run(["wget", "-r", "--no-parent", "--reject", "index.html", "-P", destination, url], check=True)
        
        - Possible approach 2:
            import os
            import requests
            from bs4 import BeautifulSoup
            from urllib.parse import urljoin

            def download_directory(url, download_path):
                if not os.path.exists(download_path):
                    os.makedirs(download_path)

                response = requests.get(url)
                soup = BeautifulSoup(response.text, 'html.parser')

                for link in soup.find_all('a'):
                    href = link.get('href')
                    if href and not href.startswith('?'):
                        download_url = urljoin(url, href)
                        download_file_path = os.path.join(download_path, href)

                        if href.endswith('/'):
                            # Recursive call to handle subdirectories
                            download_directory(download_url, download_file_path)
                        else:
                            # Download the file
                            file_response = requests.get(download_url)
                            with open(download_file_path, 'wb') as file:
                                file.write(file_response.content)
                            print(f"Downloaded {download_file_path}")

            # Usage
            download_directory('http://example.com/directory/', './downloaded_directory')


'''

import subprocess, os, sys, tempfile, shutil, re, requests
import git
import validators


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
        automatically_increment_version=False,
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
        
        if validators.url(project_directory):
            project_directory = self._clone_repository(project_directory)
            self.is_project_directory_a_url = True
        ## Check for Valid Project:
        elif not os.path.exists(project_directory):
            pt.c(' -- You must pass a legitimate project directory to try to process this!!!')
            pt.c(' -- Error: message for production:')
            raise FileNotFoundError(f'Project directory {project_directory} does not exist.')
        else:
            self.is_project_directory_a_url = False

        self.project_directory = project_directory
        
        ## Args
        self.project_directory = project_directory
        self.destination_directory = project_directory if destination_directory is None else destination_directory
        self.package_name = os.path.basename(project_directory) if package_name is None else package_name
        self.automatically_increment_version = automatically_increment_version
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
        
        self.version_number = None          ## Declared here for clarity
        self.pypi_version_number = None     ## Declared here for clarity
        
        ## Execute
        self._execute_full_workflow()

    def _clone_repository(self, url):
        temp_dir = tempfile.mkdtemp()
        print(f"Cloning {url} into {temp_dir}")
        # Extract the repository name from the URL
        repo_name = url.split('/')[-1]  # Get the last part of the URL
        if repo_name.endswith('.git'):
            repo_name = repo_name[:-4]  # Remove the '.git' extension if present
        # Create a named directory within the temporary directory
        named_dir = os.path.join(temp_dir, repo_name)
        os.makedirs(named_dir, exist_ok=True)
        git.Repo.clone_from(url, named_dir)
        return named_dir
    
    def user_options(self):
        
        self.user_options = {
            'fix_and_optimize': True, 
            'create_init_files': True, 
            'build_wheel': True, 
            'uninstall_package': True, 
            'install_package_locally': True, 
            'test_installed_package': True, 
            'uninstall_package': True, 
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
            pt.c(f'-- Finished Creating requirements.txt in {self.distribution_directory}')
        except Exception as e:
            pt.e()
            pt.ex(e)

    def setup_file_data(self):
        
        self.setup_file_manager = SetupFileManager(
            self.project_directory, 
            self.distribution_directory,
            self.package_name,
            )
        self.pyproject_data = self.setup_file_manager.get_setup_file_data()
        pt(self.pyproject_data)
        
        self.username = self.pyproject_data['author']
        self.email = self.pyproject_data['author_email']
        # pt(self.username)
        self.package_name = self.pyproject_data['package_name']
        self.version_number = self.pyproject_data['version']
        
        self.pyproject_file_path = self.pyproject_data['pyproject_file_path']
        # pt.ex()

    def verify_package_availability_status(self):
        self.verifier = PyPIVerifier(
            self.package_name, 
            self.username,
            self.email,
            self.version_number, 
            self.use_test_pypi, 
            self.use_gui, 
            self.automatically_increment_version
        )
        self.package_name, self.username, self.version_number = self.verifier.handle_verification()
        pt(self.package_name, self.username, self.version_number)
        
        # Update the pyproject.toml file with the verified or modified values
        self.setup_file_manager.modify_package_name(self.package_name)
        self.setup_file_manager.modify_owner(self.username, self.email)
        self.setup_file_manager.modify_version(self.version_number)
        
        
        # pt(self.username)

    def fix_and_optimize_package(self):
        fix_and_optimize(self.project_directory, self.distribution_directory, self.user_options)

    def build_wheel_hatch_version(self):
        '''failing
        '''
        ## Debug Log the contents of the project directory
        # print("Contents of the project directory:")
        # for root, dirs, files in os.walk(self.project_directory):
        #     for file in files:
        #         print(os.path.join(root, file))
        
        
        original_cwd = os.getcwd()
        try:
            os.chdir(self.project_directory)
            print("Current working directory:", os.getcwd())
            target_directory = os.path.abspath(self.pypi_distribution_directory)
            print(f"Target directory for build: {repr(target_directory)}")

            try:
                result = subprocess.run(
                    ## NOTE: '--target' consistently didn't work. So just build without a 
                    ## target directory, then move the wheel file afterwards.
                    ## [sys.executable, '-m', 'hatchling', 'build', '--target', target_directory],
                    [sys.executable, '-m', 'hatchling', 'build'],
                    check=True,
                    capture_output=True,
                    text=True,
                    cwd=self.project_directory,
                )
                print('1', result.stdout)
                print('2', result.stderr)
            except subprocess.CalledProcessError as e:
                print(f"Error during build with Hatch: {e}")
                print('3', e.stdout)
                print('4', e.stderr)

            wheels = [f for f in os.listdir(target_directory) if f.endswith('.whl')]
            
            if wheels:
                self.wheel_path = os.path.join(target_directory, wheels[0])
                print("Wheel built successfully with Hatch:", self.wheel_path)
            else:
                raise FileNotFoundError("No wheel file created with Hatch.")
        finally:
            os.chdir(original_cwd)

    def build_wheel(self):
        ## Debug Log the contents of the project directory
        # print("Contents of the project directory:")
        # for root, dirs, files in os.walk(self.project_directory):
        #     for file in files:
        #         print(os.path.join(root, file))
        
        original_cwd = os.getcwd()
        
        try:
            os.chdir(self.project_directory)
            print("Current working directory:", os.getcwd())
            print("self.project_directory (repr):", repr(self.project_directory))
            print("Does self.project_directory exist?", os.path.exists(self.project_directory))
            
            # Clear existing build directory to avoid using stale data
            build_dir = os.path.join(self.pypi_structure_directory, self.pypi_build_subfolder)
            if os.path.exists(build_dir):
                shutil.rmtree(build_dir)
                print(f"Cleared old build directory at {build_dir}.")
                
            # Building the wheel
            try:
                # Using the build module to build the package
                result = subprocess.run(
                    [sys.executable, '-m', 'build', '--wheel', '--outdir', self.pypi_distribution_directory],
                    check=True,
                    capture_output=True,
                    text=True
                )
                print("Build output:", result.stdout)
            except subprocess.CalledProcessError as e:
                print("Error during build:", e.stderr)
                raise
            
            # Check for the wheel file in the output directory
            wheels = [f for f in os.listdir(self.pypi_distribution_directory) if f.endswith('.whl') and self.version_number in f]
            if wheels:
                self.wheel_path = os.path.join(self.pypi_distribution_directory, wheels[0])
                print("Wheel built successfully:", self.wheel_path)
            else:
                raise FileNotFoundError(f"No wheel file created for version {self.version_number}.")
        finally:
            os.chdir(original_cwd)

    def uninstall_package(self):
        subprocess.run([sys.executable, '-m', 'pip', 'uninstall', self.package_name, '-y'], check=True)

    def install_package_locally(self):
        subprocess.run([
                'pip', 'install', self.wheel_path, 
                '--user', 
                '--force-reinstall', 
                '--no-cache-dir'], 
            check=True)

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
            print(f"Test 1 Success: The package '{self.package_name}' appears to be installed. Performing Further tests...")
        else:
            print(f"Test 1 Failure: The package '{self.package_name}' is not installed or not found by pip.")
            sys.exit(1)
        
        ## Test 2: Attempt to import the package to verify it's accessible
        try:
            __import__(self.package_name)
            print(f"Test 2 Success: The package '{self.package_name}' was successfully imported.")
        except ImportError as e:
            print(f"Test 2 Failure: Could not import the package '{self.package_name}'. Error: {e}")
            sys.exit(1)
        
        ## Test 3: Execute elsewhere to ensure the package's avaiability
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp:
            temp.write(
                f'import {self.package_name}\n'
                f'print("Test 3 Success: The package \'{self.package_name}\' is successfully being executed in a temporary test script.")\n'.encode('utf-8')
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
        
        print(f'All Tests Passed. Package "{self.package_name}" has been successfully installed.')
        print(f"'{self.package_name}'Details:\n{result_test_1.stdout}")

    def upload_package_to_pypi(self):
        if self.use_test_pypi:
            repository_url = 'https://test.pypi.org/legacy/'
            token = os.getenv(self.test_pypi_token_env_var)
        else:
            repository_url = 'https://upload.pypi.org/legacy/'
            token = os.getenv(self.pypi_token_env_var)

        ## Check if the token is available
        if not token: ## TODO: Change the 'TEST_PYPI_TOKEN' to 'test_pypi_token_env_var' etc???
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
        pt(dists)

        try:
            pt()
            twine_upload(settings, dists)
        except requests.exceptions.HTTPError as e:
            pt(e)
            if "This filename has already been used, use a different version." in str(e):
                pt()
                if self.automatically_increment_version:
                    pt()
                    self.verifier.verify_version_available()
                    self.version_number = self.verifier.auto_increment_version()
                    pt(self.version_number)
                    self.setup_file_manager.modify_version(self.version_number)
                    self.build_wheel()  # Rebuild the wheel with the new version
                    self.upload_package_to_pypi()  # Try uploading again
                else:
                    pt()
                    self.verifier.prompt_for_input("The current version has already been used. Please enter a new version:")
                    self.setup_file_manager.modify_version(self.version_number)
                    self.build_wheel()  # Rebuild the wheel with the new version
                    self.upload_package_to_pypi()  # Try uploading again
            else:
                pt()
                raise e

    def install_package_from_pypi(self):
        pypi_type = 'Test PyPI' if self.use_test_pypi else 'PyPI'
        pt.c(f'Installing Package from {pypi_type}')
        index_url = 'https://test.pypi.org/simple/' if self.use_test_pypi else 'https://pypi.org/simple'
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--index-url', index_url, self.package_name], check=True)

    def _execute_full_workflow(self):
        self.user_options()
        self.create_directories()
        self.check_or_gen_requirements()
        self.setup_file_data()
        # pt.ex()
        self.verify_package_availability_status()
        self.fix_and_optimize_package()
        self.build_wheel()
        self.uninstall_package()
        self.install_package_locally()
        self.test_installed_package() ## Test Local Wheel Package
        pt.ex()
        self.uninstall_package()
        self.upload_package_to_pypi()
        self.install_package_from_pypi()
        self.test_installed_package() ## Test Pypi intalled Package
        
        print(f'SUCCESS: Your package {self.package_name} has been created, tested, uploaded to PyPI, installed from Pypi, and tested again!')


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
    project_dirs = [
        name for name in os.listdir(main_projects_path)
        if os.path.isdir(os.path.join(main_projects_path, name)) 
        and re.match(r'[A-Z]_', name)]
    project_dirs = [os.path.join(main_projects_path, project_dir) for project_dir in project_dirs]
    
    github_url = 'https://github.com/developer-1v/SavedGithubTestProject.git'
    project_dirs.append(github_url)
    
    start_index = 0
    end_index = 1
    # start_index = -1
    # end_index = None  ## Start of 1 with None as end: will pick the last item only
    selected_projects = project_dirs[start_index:end_index]
    pt(project_dirs, selected_projects)
    
    for project_dir in selected_projects:    
        PipUniversalProjects(
            project_directory=project_dir,
            automatically_increment_version=True,
            use_standard_build_directories=True,
            use_test_pypi=True,
            # test_pypi_token_env_var='NON-EXISTANT_PYPI_TOKEN_FOR_TESTING',
        )

if __name__ == '__main__':
    test()