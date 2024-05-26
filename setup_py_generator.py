'''
NOTE: (delete?)
This file is currently a template/ idea of what I want to do. It's untested. 
- I think this functionality has been replaced by my setup_file_manager.py

'''

import os, textwrap, re, subprocess

class SetupFileManager:
    def __init__(self, directory):
        self.directory = directory
        self.setup_file_path = os.path.join(self.directory, 'setup.py')
        self.setup_file_data = ""
        self.package_name = os.path.basename(directory)
        self.version = "0.1"  # Default version
        self.requirements_path = os.path.join(self.directory, 'requirements.txt')

    def initialize_setup_file_data(self):
        if os.path.exists(self.setup_file_path):
            with open(self.setup_file_path, 'r') as file:
                self.setup_file_data = file.read()
            self.extract_package_details()
        else:
            self.setup_file_data = textwrap.dedent(f"""
                from setuptools import setup, find_packages

                setup(
                    name='{self.package_name}',
                    version='{self.version}',
                    packages=find_packages(),
                    install_requires=[],  # Add your dependencies here
                )
                """)
            with open(self.setup_file_path, 'w') as file:
                file.write(self.setup_file_data)
            self.create_requirements_file()

    def extract_package_details(self):
        name_match = re.search(r"name=['\"]([^'\"]+)['\"]", self.setup_file_data)
        version_match = re.search(r"version=['\"]([^'\"]+)['\"]", self.setup_file_data)
        if name_match:
            self.package_name = name_match.group(1)
        if version_match:
            self.version = version_match.group(1)
        if not os.path.exists(self.requirements_path):
            self.create_requirements_file()

    def create_requirements_file(self):
        if not os.path.exists(self.requirements_path):
            # Generate requirements.txt using pipreqs if it doesn't exist
            subprocess.run(['pipreqs', self.directory, '--force'])

    def find_version_in_alternative_files(self):
        # Search for version in .txt or .md files if not found in setup.py
        for root, dirs, files in os.walk(self.directory):
            for file in files:
                if 'version' in file and (file.endswith('.txt') or file.endswith('.md')):
                    with open(os.path.join(root, file), 'r') as f:
                        content = f.read()
                        version_match = re.search(r'\bversion\s*[:=]\s*([0-9.]+)', content, re.IGNORECASE)
                        if version_match:
                            self.version = version_match.group(1)
                            return
        # Fallback to main.py if no version found
        main_py_path = os.path.join(self.directory, 'main.py')
        if os.path.exists(main_py_path):
            with open(main_py_path, 'r') as file:
                content = file.read()
                version_match = re.search(r'\bversion\s*[:=]\s*([0-9.]+)', content, re.IGNORECASE)
                if version_match:
                    self.version = version_match.group(1)
