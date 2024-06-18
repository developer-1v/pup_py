from print_tricks import pt
import os, re, shutil
import toml

class SetupFileManager:
    def __init__(self, 
            project_directory, 
            distribution_directory, 
            package_name,
            version='0.1.0',
            username='developer-1v',
            email='developer-1v@gmail.com',
            packages='["."]',
        ):
        self.project_directory = project_directory
        self.distribution_directory = distribution_directory
        self.package_name = package_name
        self.version = version
        self.username = username
        self.email = email
        self.packages = packages
        
    def get_setup_file_data(self):
        # Define paths to potential configuration files
        search_pyproject_path = os.path.join(self.project_directory, 'pyproject.toml')
        search_pyproject_in_dist_dir = os.path.join(self.distribution_directory, 'pyproject.toml')
        search_setup_path = os.path.join(self.project_directory, 'setup.py')
        search_setup_in_dist_dir = os.path.join(self.distribution_directory, 'setup.py')
        search_main_py_path = os.path.join(self.project_directory, 'main.py')
        # pt(search_setup_path, search_main_py_path, search_setup_in_dist_dir)
        
        # Ensure the build_dist directory exists before attempting to copy files
        os.makedirs(self.distribution_directory, exist_ok=True)
        
        # First, try to find pyproject.toml in the project directory or distribution directory
        if os.path.exists(search_pyproject_path):
            data = self.parse_pyproject_file(search_pyproject_path)
            print("pyproject.toml found and parsed in project directory.")
            return data
        elif os.path.exists(search_pyproject_in_dist_dir):
            data = self.parse_pyproject_file(search_pyproject_in_dist_dir)
            print("pyproject.toml found and parsed in build distribution directory.")
            return data
        
        # Next, check for setup.py in the same locations
        if os.path.exists(search_setup_path):
            data = self.parse_setup_file(search_setup_path)
            print("setup.py found and parsed in project directory.")
            return data
        elif os.path.exists(search_setup_in_dist_dir):
            data = self.parse_setup_file(search_setup_in_dist_dir)
            print("setup.py found and parsed in build distribution directory.")
            return data
        
        # If no configuration files are found, check main.py for necessary data
        if os.path.exists(search_main_py_path):
            data = self.parse_main_file(search_main_py_path)
            # Assuming create_pyproject_from_template can take data to create a specific pyproject.toml
            self.create_pyproject_from_template(data)
            print("main.py found and used to create pyproject.toml in the build distribution directory.")
            return data
        
        # If no relevant files are found, create a new pyproject.toml from a template without specific data
        print("No configuration files found. Creating new pyproject.toml from template.")
        data = self.create_pyproject_from_template()
        return data

    def create_pyproject_from_template(self):
        # pt.ex()
        this_dir = os.path.dirname(__file__)
        template_path = os.path.join(this_dir, 'pyproject_template_example.toml')
        self.new_toml_path = os.path.join(self.distribution_directory, 'pyproject.toml')
        pt(template_path, self.new_toml_path)
        
        os.makedirs(self.distribution_directory, exist_ok=True)
        
        shutil.copy(template_path, self.new_toml_path)
        
        return self.update_toml_file_with_all_modifications()

    def parse_pyproject_file(self, file_path):
        """
        Parses a pyproject.toml file to extract package metadata.

        Args:
        file_path (str): The path to the pyproject.toml file.

        Returns:
        dict: A dictionary containing extracted metadata such as package name and version.
        """
        try:
            # Load and parse the pyproject.toml file
            with open(file_path, 'r') as file:
                pyproject_data = toml.load(file)

            # Extracting package metadata from the tool.poetry section if it exists
            if 'tool' in pyproject_data:
                if 'poetry' in pyproject_data['tool']:
                    poetry_data = pyproject_data['tool']['poetry']
                    return {
                        'package_name': poetry_data.get('name'),
                        'version': poetry_data.get('version'),
                        'description': poetry_data.get('description', ''),
                        'authors': poetry_data.get('authors', []),
                        'dependencies': poetry_data.get('dependencies', {}),
                        'dev_dependencies': poetry_data.get('dev-dependencies', {})
                    }
                elif 'hatch' in pyproject_data['tool']:
                    hatch_data = pyproject_data['tool']['hatch']
                    return {
                        'package_name': hatch_data.get('name'),
                        'version': hatch_data.get('version'),
                        'description': hatch_data.get('description', ''),
                        'authors': hatch_data.get('authors', []),
                        'dependencies': hatch_data.get('dependencies', {}),
                        'dev_dependencies': hatch_data.get('dev-dependencies', {})
                    }
                elif 'setuptools' in pyproject_data['tool']:
                    setuptools_data = pyproject_data['tool']['setuptools']
                    return {
                        'package_name': setuptools_data.get('name'),
                        'version': setuptools_data.get('version'),
                        'description': setuptools_data.get('description', ''),
                        'authors': setuptools_data.get('authors', []),
                        'dependencies': setuptools_data.get('install_requires', {}),
                        'dev_dependencies': setuptools_data.get('setup_requires', {})
                    }
            else:
                raise ValueError("The pyproject.toml file does not contain a recognized 'tool' section for Python packaging.")

        except Exception as e:
            print(f"Failed to parse pyproject.toml: {e}")
            raise

    def parse_setup_file(self, file_path):
        with open(file_path, 'r') as file:
            content = file.read()
        
        # Adjusting the regular expressions to handle optional spaces around equals signs
        package_name = self.extract_value(content, r'name\s*=\s*')
        version = self.extract_value(content, r'version\s*=\s*')
        username = self.extract_value(content, r'authors\s*=\s*\[\s*\{.*?name\s*:\s*"')
        # email = self.extract_value(content, r'authors\s*=\s*\[\s*\{.*?email\s*:\s*"')
        email = self.extract_value(content, r'authors\s*=\s*\[\s*\{[^}]*?email\s*:\s*"([^"]+)"')
        packages = self.extract_value(content, r'packages\s*=\s*\[')

        if package_name == '' or version == '':
            return {'package_name': None, 'version': None}
        return {
            'package_name': package_name, 
            'version': version,
            'username': username,
            'email': email,
            'packages': packages,
            'pyproject_file_path': file_path
        }

    def parse_main_file(self, file_path):
        """
        Parses a main.py file to extract basic package metadata, assuming some conventional comments or docstrings.
        
        Args:
        file_path (str): The path to the main.py file.
        
        Returns:
        dict: A dictionary containing extracted metadata such as package name and version.
        """
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                
            # Extract package name and version from conventional comments or docstrings
            package_name = self.extract_value(content, r'#\s*Package Name:\s*')
            version = self.extract_value(content, r'#\s*Version:\s*')
            description = self.extract_value(content, r'#\s*Description:\s*')
            authors = self.extract_value(content, r'#\s*Authors:\s*')
            dependencies = self.extract_value(content, r'#\s*Dependencies:\s*')

            # Convert extracted authors from string to list
            authors_list = [author.strip() for author in authors.split(',')] if authors else []

            # Convert extracted dependencies from string to dictionary
            dependencies_dict = {dep.split('==')[0].strip(): dep.split('==')[1].strip() for dep in dependencies.split(',')} if dependencies else {}

            return {
                'package_name': package_name,
                'version': version,
                'description': description,
                'authors': authors_list,
                'dependencies': dependencies_dict,
                'dev_dependencies': {}
            }

        except Exception as e:
            print(f"Failed to parse main.py: {e}")
            raise

    def extract_value(self, content, key):
        start = content.find(key) + len(key)
        if start != -1:
            end = content.find('}', start)
            if end == -1:
                end = len(content)
            value = content[start:end].strip().strip("'\"").strip()
            return value
        return None

    def update_toml_file_with_all_modifications(self):
        self.modify_package_name(self.package_name)
        self.modify_version(self.version)
        self.modify_owner(self.username, self.email)
        self.modify_packages(self.packages)
        
        return {
            'package_name': self.package_name, 
            'version': self.version,
            'username': self.username,
            'email': self.email,
            'packages': self.packages,
            'pyproject_file_path': self.new_toml_path
        }

    def modify_owner(self, new_owner, new_email):
        self.read_template()
        self.template_content = re.sub(
            r'authors\s*=\s*\[\s*\{.*?\}\s*\]', 
            f'authors = [{{name = "{new_owner}"}}, {{email = "{new_email}"}}]', 
            self.template_content)
        self.save_changes()

    def save_changes(self):
        with open(self.new_toml_path, 'w') as file:
            file.write(self.template_content)

    def read_template(self):
        with open(self.new_toml_path, 'r') as file:
            self.template_content = file.read()

    def modify_package_name(self, new_package_name):
        self.read_template()
        self.template_content = re.sub(
            r'name\s*=\s*"[^"]+"', f'name = "{new_package_name}"', self.template_content)
        self.save_changes()

    def modify_version(self, new_version):
        self.read_template()
        self.template_content = re.sub(
            r'version\s*=\s*"[^"]+"', f'version = "{new_version}"', self.template_content)
        self.save_changes()

    def modify_packages(self, new_packages):
        # Get the parent directory of the current distribution directory
        parent_directory = os.path.dirname(self.distribution_directory)
        escaped_parent_directory = parent_directory.replace("\\", "/")  # Use forward slashes for paths

        # Split the escaped parent directory to separate the base path and the target directory
        path_parts = escaped_parent_directory.split('/')
        base_path = '/'.join(path_parts[:-1])  # Everything except the last part
        target_directory = path_parts[-1]  # The last part of the path

        self.read_template()
        self.template_content = re.sub(
            r'packages\s*=\s*\{\s*find\s*=\s*\{\s*where\s*=\s*\["[^"]*"\],\s*include\s*=\s*\["[^"]*"\]\s*\}\s*\}',
            # f'packages = {{find = {{where = [".."], include = ["{target_directory}/*"]}}}}',
            f'packages = {{find = {{where = [".."], include = ["{self.package_name}*"]}}}}',
            self.template_content)
        self.save_changes()




if __name__ == '__main__':

    base_path = r'C:\.PythonProjects\SavedTests\_test_projects_for_building_packages\projects'
    os.makedirs(base_path, exist_ok=True)
    
    ## Dynamically get names of all test projects that start with a capital letter and underscore:
    project_directories = [name for name in os.listdir(base_path)
                    if os.path.isdir(os.path.join(base_path, name)) and re.match(r'[A-Z]_', name)]

    ## TODO DELETE: temporary testing of individual projects
    project_directories = [
        # 'A_with_nothing',
        'B_with_pyproject_toml_good',
    ]
    
    
    for project_directory in project_directories:    
        setup_file_manager = SetupFileManager(
            project_directory=os.path.join(base_path, project_directory),
            distribution_directory=os.path.join(base_path, project_directory, 'build_dist'),
            package_name=project_directory,
            version='0.1.0',
            username='developer-1v',
            packages='["."]',
        )
        setup_data = setup_file_manager.get_setup_file_data()
        pt(setup_data)





'''

old:
    # def create_setup_from_template(self):
    #     this_dir = os.path.dirname(__file__)
    #     template_path = os.path.join(this_dir, 'setup_template_example.py')
    #     utilities_path = os.path.join(this_dir, 'setup_utilities.py')
    #     new_setup_path = os.path.join(self.distribution_directory, 'setup.py')
    #     new_utilities_path = os.path.join(self.distribution_directory, 'setup_utilities.py')
    #     pt(template_path, utilities_path, new_setup_path, new_utilities_path)
        
    #     os.makedirs(self.distribution_directory, exist_ok=True)
        
    #     ## make copies
    #     shutil.copy(utilities_path, new_utilities_path)
    #     shutil.copy(template_path, new_setup_path)

    #     ## modify the copied setup.py
    #     with open(new_setup_path, 'r') as file:
    #         template_content = file.read()
        
    #     modified_content = template_content.replace('{{package_name}}', 'example_package').replace('{{version}}', '0.1.0')
        
    #     with open(new_setup_path, 'w') as file:
    #         file.write(modified_content)

    #         return {'package_name': 'example_package', 'version': '0.1.0'}


'''