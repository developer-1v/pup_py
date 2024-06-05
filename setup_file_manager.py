from print_tricks import pt
import os, re, shutil

class SetupFileManager:
    def __init__(self, project_directory, distribution_directory):
        self.project_directory = project_directory
        self.distribution_directory = distribution_directory

    def get_setup_file_data(self):
        search_setup_path = os.path.join(self.project_directory, 'setup.py')
        search_main_py_path = os.path.join(self.project_directory, 'main.py')
        search_setup_in_dist_dir = os.path.join(self.distribution_directory, 'setup.py')
        pt(search_setup_path, search_main_py_path, search_setup_in_dist_dir)
        
        ## Ensure the build_dist directory exists before attempting to copy files
        os.makedirs(self.distribution_directory, exist_ok=True)
        
        if os.path.exists(search_setup_path):
            data = self.parse_setup_file(search_setup_path)
            if data['package_name'] is None or data['version'] is None:
                print("Invalid setup.py found. Creating a new one from template.")
                data = self.create_setup_from_template()
                new_setup_path = search_setup_in_dist_dir
                print("New setup.py created from template.")
                return data, new_setup_path
            else:
                print("Valid setup.py found and parsed.")
                pt(data, search_setup_path)
                # pt.ex()
                return data, search_setup_path
        elif os.path.exists(search_setup_in_dist_dir):
            data = self.parse_setup_file(search_setup_in_dist_dir)
            print("Setup.py found and parsed in build distribution directory.")
            return data, search_setup_in_dist_dir
        elif os.path.exists(search_main_py_path):
            data = self.parse_setup_file(search_main_py_path)
            # Create setup.py in the build distribution directory
            shutil.copy(search_main_py_path, search_setup_in_dist_dir)
            print("Main.py found and used to create setup.py in the build distribution directory.")
            return data, search_setup_in_dist_dir
        else:
            data = self.create_setup_from_template()
            new_setup_path = search_setup_in_dist_dir  # Use the predefined path in the distribution directory
            print("No setup.py or main.py found. Created new setup.py from template.")
            return data, new_setup_path

    def parse_setup_file(self, file_path):
        with open(file_path, 'r') as file:
            content = file.read()
        package_name = self.extract_value(content, 'name=')
        version = self.extract_value(content, 'version=')
        if package_name == '' or version == '':
            return {'package_name': None, 'version': None}
        return {'package_name': package_name, 'version': version}

    def extract_value(self, content, key):
        start = content.find(key) + len(key)
        if start != -1:
            end = content.find(',', start)
            if end == -1:
                end = len(content)
            value = content[start:end].strip().strip("'\"")
            return value
        return None

    def create_setup_from_template(self):
        this_dir = os.path.dirname(__file__)
        template_path = os.path.join(this_dir, 'setup_template_example.py')
        utilities_path = os.path.join(this_dir, 'setup_utilities.py')
        new_setup_path = os.path.join(self.distribution_directory, 'setup.py')
        new_utilities_path = os.path.join(self.distribution_directory, 'setup_utilities.py')
        pt(template_path, utilities_path, new_setup_path, new_utilities_path)
        
        os.makedirs(self.distribution_directory, exist_ok=True)
        
        ## make copies
        shutil.copy(utilities_path, new_utilities_path)
        shutil.copy(template_path, new_setup_path)

        ## modify the copied setup.py
        with open(new_setup_path, 'r') as file:
            template_content = file.read()
        
        modified_content = template_content.replace('{{package_name}}', 'example_package').replace('{{version}}', '0.1.0')
        
        with open(new_setup_path, 'w') as file:
            file.write(modified_content)

            return {'package_name': 'example_package', 'version': '0.1.0'}


if __name__ == '__main__':

    base_path = r'C:\.PythonProjects\SavedTests\_test_projects_for_building_packages\projects'
    os.makedirs(base_path, exist_ok=True)
    
    ## Dynamically get names of all test projects that start with a capital letter and underscore:
    project_directories = [name for name in os.listdir(base_path)
                    if os.path.isdir(os.path.join(base_path, name)) and re.match(r'[A-Z]_', name)]

    ## TODO DELETE: temporary testing of individual projects
    project_directories = ['A_with_nothing',
                    ]
    
    
    for project_directory in project_directories:    
        setup_file_manager = SetupFileManager(
            project_directory=os.path.join(base_path, project_directory),
            distribution_directory=os.path.join(base_path, project_directory, 'build_dist')
        )
        setup_data = setup_file_manager.get_setup_file_data()
    pt(setup_data)

