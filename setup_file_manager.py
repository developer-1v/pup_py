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
        search_setup_path = os.path.join(self.project_directory, 'setup.py')
        search_main_py_path = os.path.join(self.project_directory, 'main.py')
        search_setup_in_dist_dir = os.path.join(self.distribution_directory, 'setup.py')
        search_toml_in_dist_dir = os.path.join(self.distribution_directory, 'pyproject.toml')  # Path for pyproject.toml
        pt(search_setup_path, search_main_py_path, search_setup_in_dist_dir)
        
        ## Ensure the build_dist directory exists before attempting to copy files
        os.makedirs(self.distribution_directory, exist_ok=True)
        
        if os.path.exists(search_setup_path):
            data = self.parse_setup_file(search_setup_path)
            if data['package_name'] is None or data['version'] is None:
                print("Invalid setup.py found. Creating a new one from template.")
                data = self.create_pyproject_from_template()
                print("New pyproject.toml created from template.")
                return data
            else:
                print("Valid setup.py found and parsed.")
                pt(data, search_setup_path)
                return data
        elif os.path.exists(search_setup_in_dist_dir):
            data = self.parse_setup_file(search_setup_in_dist_dir)
            print("Setup.py found and parsed in build distribution directory.")
            return data
        elif os.path.exists(search_main_py_path):
            data = self.parse_setup_file(search_main_py_path)
            shutil.copy(search_main_py_path, search_setup_in_dist_dir)
            print("Main.py found and used to create setup.py in the build distribution directory.")
            return data
        else:
            data = self.create_pyproject_from_template()
            print("No setup.py or main.py found. Created new pyproject.toml from template.")
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
        'A_with_nothing',
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