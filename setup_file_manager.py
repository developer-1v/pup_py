from print_tricks import pt
import os
import shutil

class SetupFileManager:
    def __init__(self, project_dir, build_dist_dir):
        self.project_dir = project_dir
        self.build_dist_dir = build_dist_dir

    def get_setup_file_data(self):
        search_setup_path = os.path.join(self.project_dir, 'setup.py')
        search_main_py_path = os.path.join(self.project_dir, 'main.py')
        search_setup_in_dist_dir = os.path.join(self.build_dist_dir, 'setup.py')
        pt(search_setup_path, search_main_py_path, search_setup_in_dist_dir)
        
        if os.path.exists(search_setup_path):
            data = self.parse_setup_file(search_setup_path)
            return data, search_setup_path
        elif os.path.exists(search_setup_in_dist_dir):
            data = self.parse_setup_file(search_setup_in_dist_dir)
            return data, search_setup_in_dist_dir
        elif os.path.exists(search_main_py_path):
            data = self.parse_setup_file(search_main_py_path)
            # Create setup.py in the build distribution directory
            shutil.copy(search_main_py_path, search_setup_in_dist_dir)
            return data, search_setup_in_dist_dir
        else:
            data = self.create_setup_from_template()
            new_setup_path = search_setup_in_dist_dir  # Use the predefined path in the distribution directory
            return data, new_setup_path

    def parse_setup_file(self, file_path):
        with open(file_path, 'r') as file:
            content = file.read()
        package_name = self.extract_value(content, 'name=')
        version = self.extract_value(content, 'version=')
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
        template_path = os.path.join(this_dir, 'setup_template.py')
        utilities_path = os.path.join(this_dir, 'setup_utilities.py')
        new_setup_path = os.path.join(self.build_dist_dir, 'setup.py')
        new_utilities_path = os.path.join(self.build_dist_dir, 'setup_utilities.py')
        pt(template_path, utilities_path, new_setup_path, new_utilities_path)
        
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
    setup_file_manager = SetupFileManager(
        project_dir=r'C:\.PythonProjects\SavedTests\test_package_for_builds',
        build_dist_dir=r'C:\.PythonProjects\SavedTests\test_package_for_builds\build_dist'
        )
    setup_data = setup_file_manager.get_setup_file_data()
    pt(setup_data)

