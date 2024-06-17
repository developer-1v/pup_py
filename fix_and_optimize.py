import os, json
from print_tricks import pt



    

import os, json

def find_py_directories(project_dir, excludes):
    """
    Walks through the project directory to find directories containing .py files
    that need an __init__.py file but do not already have one.
    """
    py_directories = []
    for root, dirs, files in os.walk(project_dir):
        valid_dirs = []
        for d in dirs:
            full_path = os.path.join(root, d)
            if not (d.startswith('.') or d.startswith('__')) and not any(excluded == os.path.basename(full_path) for excluded in excludes):
                valid_dirs.append(d)
        dirs[:] = valid_dirs  # Update the list of directories with those that are not excluded

        if any(file.endswith('.py') for file in files) and '__init__.py' not in files:
            py_directories.append(root)
    return py_directories

def create_init_files(directories, distribution_dir):
    """
    Creates an __init__.py file in each directory specified in the directories list.
    """
    created_init_in_dirs = []
    for directory in directories:
        init_path = os.path.join(directory, '__init__.py')
        open(init_path, 'a').close()  # Create an empty __init__.py file
        print(f'Created __init__.py in {directory}')
        created_init_in_dirs.append(directory)

    # Save the paths of created __init__.py files, so we can reverse this later if needed
    created_init_files_json = os.path.join(distribution_dir, 'created_init_files.json')
    with open(created_init_files_json, 'w') as f:
        json.dump(created_init_in_dirs, f)

def create_init_files_main(project_dir, distribution_dir, user_options):
    _excludes = [
        "__pycache__", # python cache
        ".directory", # directory
        ".Trashes", # trash
        ".Python", # python
        ".pybuilder", # pybuilder
        ".ipynb_checkpoints", # ipynb checkpoints
        ".venv", # virtual environment
        ".git", # git repository
        ".vscode", # Visual Studio Code
        ".idea",  # JetBrains PyCharm
        ".eclipse",  # Eclipse
        ".classpath",  # Eclipse
        ".project",  # Eclipse
        ".settings",  # Eclipse
        ".DS_Store",  # macOS Desktop Services Store
        "build_dist", # pup_py and easy exe creator (name?)
        "build", # common build directory
        "dist", # common dist directory
        "env",  # Common virtualenv directory
        "venv",  # Common virtualenv directory
        "bin",  # Common for executables and scripts
        "obj",  # Common build output directory
        "out",  # Common build output directory
        "lib",  # Common library code directory
        "libs",  # Common library code directory
        "node_modules",  # Node.js modules directory
        ".npm",  # Node.js package manager cache
        ".cache",  # Common cache directory
        ".next",  # Next.js build output
        "target",  # Maven build directory
        ".metadata",  # Used by various tools to store metadata
        ".gradle",  # Gradle cache and settings
        ".tmp",  # Common temporary directory
        "tmp",  # Common temporary directory
        "temp",  # Common temporary directory
        ".serverless",  # Serverless framework
        ".terraform",  # Terraform module cache
    ]
    additional_excludes = user_options.get('excluded_folders', [])
    if additional_excludes:
        _excludes.extend(additional_excludes)

    directories_needing_init = find_py_directories(project_dir, _excludes)
    create_init_files(directories_needing_init, distribution_dir)

def remove_init_files(project_dir, distribution_dir):
    '''Created in case a user needs to reverse/remove anything that my 
    fix and optimzie has done
    
    '''
    created_init_files_json = os.path.join(distribution_dir, 'created_init_files.json')
    
    ## Load the paths of created __init__.py files
    try:
        # os.makedirs(created_init_files_json, exist_ok=True)  # This will create the directory if it does not exist
        with open(created_init_files_json, 'r') as f:
            created_init_files = json.load(f)
    except FileNotFoundError:
        print('No created_init_files.json found in build_dist folder')
        return

    for root, dirs, files in os.walk(project_dir):
        if '__init__.py' in files:
            init_path = os.path.join(root, '__init__.py')
            # Remove only if the file is in the list of created files
            if init_path in created_init_files:
                os.remove(init_path)
                print(f'Removed __init__.py from {root}')
                created_init_files.remove(init_path)

    ## Update the list after removal
    with open(created_init_files_json, 'w') as f:
        json.dump(created_init_files, f)

def fix_and_optimize(project_dir, distribution_dir, user_options):
    create_init_files_main(project_dir, distribution_dir, user_options)

def remove_fixes_and_optimizations(project_dir, distribution_dir):
    remove_init_files(project_dir, distribution_dir)

if __name__ == "__main__":

    dir = r'C:\.PythonProjects\SavedTests\_test_projects_for_building_packages\projects\A_with_nothing'
    fix_and_optimize(
        project_dir=dir,
        distribution_dir=dir,
        user_options={'excluded_folders': ['']})
    
    pt.c('\n - Successfully fixed and optimized your project!')
    
    input('Press enter to remove fixes and optimizations')
    
    remove_fixes_and_optimizations(
        project_dir=dir,
        distribution_dir=dir
        )

