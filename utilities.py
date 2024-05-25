import subprocess

def read_file(file_path):
    """Reads content from a file."""
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return ''

def generate_requirements():
    """Generates requirements.txt if it does not exist and returns its contents."""
    requirements_path = 'requirements.txt'
    try:
        requirements = read_file(requirements_path)
        if not requirements:
            raise FileNotFoundError
    except FileNotFoundError:
        # Attempt to generate requirements using pipreqs
        try:
            with open(requirements_path, 'w') as f:
                subprocess.run(['pipreqs', '--savepath', requirements_path], stdout=f, check=True)
            requirements = read_file(requirements_path)
        except subprocess.CalledProcessError:
            # Fallback to pip freeze if pipreqs fails
            try:
                with open(requirements_path, 'w') as f:
                    subprocess.run(['pip', 'freeze'], stdout=f, check=True)
                requirements = read_file(requirements_path)
            except subprocess.CalledProcessError:
                requirements = ''
    return requirements
