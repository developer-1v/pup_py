''' Blinking Cursor in cmd '''

import sys
import time
import msvcrt

def blinking_cursor(prompt, symbols):
    try:
        sys.stdout.write(prompt)
        sys.stdout.flush()
        input_text = ""
        index = 0
        while True:
            if msvcrt.kbhit():
                char = msvcrt.getwch()  # Get the character
                if char == '\r':  # Enter key is pressed
                    sys.stdout.write("\r" + prompt + input_text + " " * len(symbols[index % len(symbols)]))  # Clear last symbol
                    sys.stdout.flush()
                    break
                elif char == '\x08':  # Backspace is handled
                    input_text = input_text[:-1]  # Remove last character
                    sys.stdout.write("\r" + prompt + input_text + " " * (len(symbols[index % len(symbols)]) - 1))
                    sys.stdout.flush()
                else:
                    input_text += char
                    sys.stdout.write("\r" + prompt + input_text + symbols[index % len(symbols)])
                    sys.stdout.flush()
            else:
                sys.stdout.write("\r" + prompt + input_text + symbols[index % len(symbols)])
                sys.stdout.flush()
                index += 1
                time.sleep(0.5)
        return input_text
    except KeyboardInterrupt:
        return ""

if __name__ == "__main__":
    # Test with simple cursor blink
    user_input_simple = blinking_cursor("Enter your input: ", [" ", "_"])
    print("\nYou entered with simple blink:", user_input_simple)

    # Test with complex pattern
    user_input_complex = blinking_cursor("Enter your input: ", ["|", "/", "-", "\\"])
    print("\nYou entered with complex pattern:", user_input_complex)



'''Find packages in a project'''

# import os
# import setuptools

# def list_directory_contents(directory):
#     # List all files and directories in the project directory
#     contents = os.listdir(directory)
#     print("Contents of the project directory:")
#     for item in contents:
#         print(item)

#     # Check for Python files specifically
#     python_files = [file for file in contents if file.endswith('.py')]
#     print("\nPython files in the project directory:")
#     for py_file in python_files:
#         print(py_file)

#     # If no Python files are found
#     if not python_files:
#         print("\nNo Python files found in the project directory. This is likely why the package cannot be imported.")

# def find_and_print_packages(directory):
#     # Use setuptools to find packages in the specified directory
#     # Include the root directory if necessary
#     found_packages = setuptools.find_packages(where=directory, include=["*"])
#     print("\nFound packages:", found_packages)

# def main():
#     project_dir = r"C:\.PythonProjects\SavedTests\_test_projects_for_building_packages\projects\A_with_nothing"
#     list_directory_contents(project_dir)
#     find_and_print_packages(project_dir)

# if __name__ == '__main__':
#     main()




'''Inspect the wheel to verify what's inside'''
# import zipfile
# import os
# import subprocess

# def unzip_wheel(wheel_path, extract_to):
#     with zipfile.ZipFile(wheel_path, 'r') as zip_ref:
#         zip_ref.extractall(extract_to)
#     print(f"Wheel extracted to: {extract_to}")

# def list_wheel_contents(wheel_path):
#     with zipfile.ZipFile(wheel_path, 'r') as zip_ref:
#         for file_info in zip_ref.infolist():
#             print(file_info.filename)

# def unpack_and_inspect_wheel(wheel_path, output_directory):
#     # Unpack wheel using wheel command-line tool
#     subprocess.run(['wheel', 'unpack', wheel_path, '-d', output_directory], check=True)
#     print(f"Wheel unpacked to: {output_directory}")

#     # Inspect wheel using wheel command-line tool
#     result = subprocess.run(['wheel', 'inspect', wheel_path], capture_output=True, text=True)
#     print("Wheel metadata:")
#     print(result.stdout)

# def main(wheel_path):
#     extract_to = 'extracted_wheel'
#     output_directory = 'unpacked_wheel'

#     # Ensure output directories do not exist
#     for directory in [extract_to, output_directory]:
#         if os.path.exists(directory):
#             os.rmdir(directory)

#     # Perform actions
#     unzip_wheel(wheel_path, extract_to)
#     list_wheel_contents(wheel_path)
#     unpack_and_inspect_wheel(wheel_path, output_directory)

# if __name__ == '__main__':
#     main(r'c:\.pythonprojects\savedtests\_test_projects_for_building_packages\projects\a_with_nothing\dist\a_with_nothing-0.1.0-py3-none-any.whl')


# ''' print out the contents of the directories for AI assitance'''
# # import os

# # Directory path
# project_dir = r"C:\.PythonProjects\SavedTests\_test_projects_for_building_packages\projects\A_with_nothing"

# # List all files and directories in the project directory
# contents = os.listdir(project_dir)
# print("Contents of the project directory:")
# for item in contents:
#     print(item)

# # Check for Python files specifically
# python_files = [file for file in contents if file.endswith('.py')]
# print("\nPython files in the project directory:")
# for py_file in python_files:
#     print(py_file)

# # If no Python files are found
# if not python_files:
#     print("\nNo Python files found in the project directory. This is likely why the package cannot be imported.")