'''One click pip Solution: 

    - Preps code for distribution
        - gets rid of debug statements, gets rid of "if name is main", etc. 
        - creates an __init__ and a print_tricks_debugger
    - Builds the wheel
    - uninstalls old pt
    - installs new local wheel
    - tests the local wheel
    - uninstalls the local wheel
    - uploads to pypi
    - installs the uploaded pypi version

    '''
import subprocess, os, time, glob, tempfile, pkg_resources, site, difflib
from print_tricks import pt, C

function_steps_counter = [0]

def main():
    create_init()
    create_wheel()
    uninstall()
    newest_file = local_pip_install()
    
    # pt.ex()
    
    uninstall()
    pypi_upload(newest_file)    
    pypi_install(newest_file)

def get_setup_info():
    setup_file = f'{os.path.dirname(os.path.abspath(__file__))}\\setup.py'
    ## pt(setup_file)
    version = ''
    file_path = f'{os.path.dirname(os.path.abspath(__file__))}\print_tricks\__init__.py'
    with open(file_path, 'r') as f:
        for line in f:
            if 'version' in line:
                version_line = line
                break

    version = version_line.split('version')[1].split()[0]

    name_line = ''
    with open(setup_file, 'r') as f:
        for line in f:
            if line.startswith('name'):
                name_line = line
                break
    package_name = name_line.split('=')[1].split()[0].replace('"', '').replace("'", "")

    # cwd1 = pt.l()
    cwd2 = os.getcwd()
    cwd3 = fr'{cwd2}\DevelopmentFiles'
    # pt(cwd1, cwd2, cwd3)

    return setup_file, version, file_path, package_name, cwd3

setup_file, version, file_path, package_name, cwd = get_setup_info()

def test_package():
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp:
        temp.write(
            b'from print_tricks import pt\n'
            b'pt.c("============ Testing the installed package ===========")\n'
            b'## pt(1)\n'
            b'g=32.322\n'
            b'## pt(g)\n'
        )
        temp_file_name = temp.name
    try:
        subprocess.run(["python", temp_file_name], check=True)
    finally:
        os.remove(temp_file_name)

def pip_install(commands, num_times=7):
    for i in range(7):
        try:
            subprocess.run(commands, check=True)
            pt.c(f"{commands} - installed successfully!")
            return True
        except subprocess.CalledProcessError:
            pt.c(f"Attempt {i+1}: {commands} - installation failed.")
            time.sleep(.75)
    pt.c(f"{commands} - installation failed after {num_times} attempts.")
    return False

def create_init():

    function_steps_counter[0] += 1
    pt.c(f'----------------- {function_steps_counter} create_init -----------------')
    ## Run my Deploy.py code to convert print_tricks to __init__.py and print_tricks_debugger.py
    commands_1 = ["cmd", "/c", "cd", cwd, "&", "python", "create_init.py"]
    subprocess.run(commands_1, check=True)

def create_wheel():
    function_steps_counter[0] += 1
    pt.c(f'----------------- {function_steps_counter} run setup to create wheel -----------------')

    commands_2 = ["cmd", "/c", "cd", cwd, "&", "python", "setup.py", "bdist_wheel"]
    subprocess.run(commands_2, check=True)

def uninstall():
    function_steps_counter[0] += 1
    pt.c(f'----------------- {function_steps_counter} uninstall -----------------')

    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp:
        temp.write(f'import subprocess; subprocess.run(["pip", "uninstall", "-y", "{package_name}"], check=True)'.encode())
        temp_file_name = temp.name

    try:
        subprocess.run(["python", temp_file_name], check=True)
    finally:
        os.remove(temp_file_name)
    
    site_packages_dirs = site.getsitepackages()

    # pt(site_packages_dirs, package_name)
    for dir in site_packages_dirs:
        if os.path.exists(os.path.join(dir, package_name)):
            print(f"Warning: The package '{package_name}' should have been uninstalled but it has not fully been removed. "
                    f"You may need to remove this package manually"
            )
        else:
            # Get all package names in the directory
            package_names = os.listdir(dir)
            
            close_matches = difflib.get_close_matches(package_name, package_names, n=1, cutoff=0.5)
            if close_matches:
                similarity_ratio = difflib.SequenceMatcher(None, package_name, close_matches[0]).ratio()
                pt(similarity_ratio)
                pt.c(f"Warning: A package with a name close to '{package_name}' was found: {close_matches[0]} "
                        f"With a match of {similarity_ratio:.0%}. "
                        f"You may need to remove this package manually"
                )

def local_pip_install():
    function_steps_counter[0] += 1
    pt.c(f'----------------- {function_steps_counter} local pip install -----------------')
    ## local install & test
    list_of_files = glob.glob(f'{cwd}/dist/*.whl')
    newest_file = max(list_of_files, key=os.path.getmtime)
    commands_4 = ["pip", "install", newest_file]
    subprocess.run(commands_4, check=True)

    test_package()

    pt.c("Success: Newest Print Tricks has been locally installed to this machine")
    return newest_file

def pypi_upload(newest_file):
    function_steps_counter[0] += 1
    pt.c(f'----------------- {function_steps_counter} pypi upload -----------------')


    ## Pypi.org upload via twine
    
    pypi_token = os.getenv("PYPI_TOKEN")
    if not pypi_token:
        raise Exception("PyPI token not found. Please set the PYPI_TOKEN environment variable.")
    
    commands_6 = ["twine", "upload", newest_file, "--username", "__token__", "--password", pypi_token]
    subprocess.run(commands_6, check=True)



def test_pypi_upload():
    ## test pypi upload via Twine
    # twine_username = "__token__"
    # pypi_token = os.getenv("test.pypi.org_Token")
    # commands_4 = ["twine", "upload", "--repository-url", "https://test.pypi.org/legacy/", newest_file, "--username", twine_username, "--password", pypi_token]
    # subprocess.run(commands_4, check=True)
    
    ## Install test pypi version
    # commands_install_new = ["pip", "install", "--index-url", "https://test.pypi.org/simple/", "--upgrade", "--no-cache-dir", 
    #                         f"{package_name}"]
    # subprocess.run(commands_install_new, check=True)
    
    ...
    
def pypi_install(newest_file):
    function_steps_counter[0] += 1
    pt.c(f'----------------- {function_steps_counter} pypi install -----------------')
    ## Install Pypi version
    commands_7_install_new = ''

    ## pt(newest_file, version)
    if version in newest_file:
        sub_version = newest_file.split(version)[1].split('-py3')[0]
    else:
        print(f"Version {version} not found in {newest_file}")
        sub_version = ''
    ## pt(newest_file, sub_version, package_name)
    commands_7_install_new = ["pip", "install", f"{package_name}=={version}{sub_version}", "--upgrade", "--no-cache-dir"]
    did_it_work = pip_install(commands_7_install_new, num_times=7)

    if not did_it_work:
        pt.c(f'Error > Exception occured when trying to pip install the newest file using the sub version.'
            f'Attempting to install via the name {package_name} only: ')
        commands_7_install_new = ["pip", "install", f"{package_name}", "--upgrade", "--no-cache-dir"]
        subprocess.run(commands_7_install_new, check=False)

    test_package()
    
    pt.c(colors=C.t2, string="\nSuccess: Newest Print Tricks has been uploaded to pypi and installed to this machine")

main()


