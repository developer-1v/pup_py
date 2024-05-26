from print_tricks import pt
import os
import shutil

class SetupFileManager:
    def __init__(self, project_dir, build_dist_dir):
        self.project_dir = project_dir
        self.build_dist_dir = build_dist_dir
        self.setup_file_data = self.get_setup_file_data()

    def get_setup_file_data(self):
        setup_file_path = os.path.join(self.build_dist_dir, 'setup.py')
        main_py_path = os.path.join(self.build_dist_dir, 'main.py')
        pt(setup_file_path, main_py_path)
        
        if os.path.exists(setup_file_path):
            return self.parse_setup_file(setup_file_path)
        elif os.path.exists(main_py_path):
            return self.parse_setup_file(main_py_path)
        else:
            return self.create_setup_from_template()

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
        
        ## make copies
        shutil.copy(utilities_path, new_utilities_path)
        shutil.copy(template_path, new_setup_path)

        ## modify the copied setup.py
        with open(new_setup_path, 'r') as file:
            template_content = file.read()
            
        modified_content = template_content.replace('{{package_name}}', 'example_package').replace('{{version}}', '0.1.0')
        
        with open(new_setup_path, 'w') as file:
            file.write(modified_content)

        ## Debugging output
        pt(template_path, utilities_path)
        pt(new_setup_path)

        return {'package_name': 'example_package', 'version': '0.1.0'}


if __name__ == '__main__':
    setup_file_manager = SetupFileManager(
        project_dir=r'C:\.PythonProjects\SavedTests\test_package_for_builds',
        build_dist_dir=r'C:\.PythonProjects\SavedTests\test_package_for_builds\build_dist'
        )
    setup_data = setup_file_manager.get_setup_file_data()
    pt(setup_data)

