import subprocess
import os

def build_package():
    # Build the package using setuptools
    subprocess.run(["python", "-m", "build"], check=True)

def uninstall_package():
    # Uninstall the package if it exists, ignoring errors if the package is not installed
    subprocess.run(["pip", "uninstall", "test_pyproject_build_mre", "-y"], check=False)

def install_package():
    # Install the package using pip with the --user flag
    subprocess.run(["pip", "install", ".", "--user"], check=True)
    print('\n\n')

def verify_installation():
    # Attempt to import the installed package
    print('\n\n')
    # try:
    #     import test_pyproject_build_mre
    #     print("Package 'test_pyproject_build_mre' has been successfully installed and is functional.")
    #     subprocess.run(['pip', 'show', 'test_pyproject_build_mre'], check=True)
    # except ImportError:
    #     print("Failed to import 'test_pyproject_build_mre'. Installation was not successful.")
    
    print('\n\n')
    try:
        import test_pyproject_build_mre
        print("Package 'A' has been successfully installed, and 'test_pyproject_build_mre' is importable and is functional.")
        subprocess.run(['pip', 'show', 'test_pyproject_build_mre'], check=True)
    except ImportError:
        print("Failed to import 'A'. Installation was not successful.")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    uninstall_package()  # Uninstall any existing versions first
    build_package()
    install_package()
    verify_installation()