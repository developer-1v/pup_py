import requests
from print_tricks import pt

class PyPIVerifier:
    def __init__(self, 
            package_name, 
            username, 
            version, 
            use_test_pypi=False, 
            use_gui=False,
            automatically_increment_version=False
            ):
        self.package_name = package_name
        self.version_number = version
        self.username = username
        # pt(self.username)
        self.automatically_increment_version = automatically_increment_version
        base_url = "https://test.pypi.org/pypi" if use_test_pypi else "https://pypi.org/pypi"
        self.use_gui = use_gui
        self.api_url = f"{base_url}/{package_name}/json"
        self.pypi_owners = []  # New attribute to store the list of maintainers
        
        self.pypi_version_number = None

    def prompt_for_input(self, prompt_message, input_type='text'):
        """
        Generic method to prompt user for input. Adapts to GUI or CLI based on configuration.
        Adds a blinking cursor when waiting for input in CLI.
        """
        if self.use_gui:
            ## GUI placeholder
            import tkinter as tk
            from tkinter import simpledialog
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            user_input = simpledialog.askstring("Input", prompt_message)
            return user_input
        else:
            ## CLI input with blinking cursor
            import sys
            import time

            # Enable blinking cursor
            sys.stdout.write('\033[?25h')  # CSI ? 25 h - Show cursor
            sys.stdout.flush()
            user_input = input(prompt_message)
            # Disable blinking cursor after input
            sys.stdout.write('\033[?25l')  # CSI ? 25 l - Hide cursor
            sys.stdout.flush()

            return user_input

    def handle_verification(self, attempt=0):
        max_attempts = 5  # Maximum number of attempts before stopping recursion
        if pt.after(3):
            pt.ex()
        if attempt >= max_attempts:
            print("Maximum attempts reached. Exiting verification process.")
            return None  # Or handle this case as needed

        is_new_package, is_our_package, is_version_available, message = self.check_package_status()
        print(message)
        
        if not is_our_package:
            choice = self.prompt_for_input("Package name might be taken or username might be incorrect. Choose an option:\n1. Change package name\n2. Change username\nEnter choice (1 or 2):", input_type='choice')
            if choice == '1':
                new_package_name = self.prompt_for_input("Enter a new package name:")
                if new_package_name:
                    self.package_name = new_package_name
                    return self.handle_verification(attempt + 1)
            elif choice == '2':
                new_username = self.prompt_for_input("Enter a new username:")
                if new_username:
                    self.username = new_username
                    return self.handle_verification(attempt + 1)
                
        if not is_version_available:
            if self.automatically_increment_version:
                self.version_number = self.auto_increment_version()
            else:
                self.version_number = self.prompt_for_input("Enter a new version number:")
            
            return self.handle_verification(attempt + 1)
        
        return self.package_name, self.username, self.version_number

    def check_package_status(self, debug=True):
        is_new_package = self.verify_new_package()
        if is_new_package:
            pt()
            is_our_package = True
            is_version_available = True
        else:
            pt()
            is_our_package = self.verify_package_owner()
            is_version_available, self.pypi_version_number = self.verify_version_available() if is_our_package else False

        if debug:
            pt(is_new_package,
                is_our_package,
                self.username,
                self.pypi_owners,
                is_version_available,
                self.version_number,
                self.pypi_version_number
            )

        if is_new_package:
            message = f"Package name '{self.package_name}' is available and can be claimed."
        elif is_our_package:
            if is_version_available:
                message = f"This is an update to an existing package '{self.package_name}' that we own, and the version '{self.version_number}' is available."
            else:
                message = f"This is an update to an existing package '{self.package_name}' that we own, but the version '{self.version_number}' already exists. Please type in a different version number directly here: (or exit this, and change it in your setup/pyproject file)"
        else:
            owner_info = f"The owner is '{self.pypi_owners[0]}'" if self.pypi_owners else "No owner information available"
            message = f"The package name '{self.package_name}' is taken and you, '{self.username}', are not the owner. {owner_info}. Please choose a different package name here: (or exit this, and change it in your setup/pyproject file)"

        
        return is_new_package, is_our_package, is_version_available, message

    def verify_new_package(self):
        response = requests.get(self.api_url)

        if response.status_code == 200:
            return False  # Package name is already taken
        elif response.status_code == 404:
            return True  # Package name is available
        else:
            response.raise_for_status()

    def verify_package_owner(self):
        response = requests.get(self.api_url)
        if response.status_code == 200:
            data = response.json()
            # pt(data)
            # pt.ex()
            # Safely access the 'maintainers' key using get() to avoid KeyError
            author = data['info'].get('author', [])
            # self.pypi_owners = [author['username'] for author in authors]
            # pt(self.username, author, self.username in  author)
            
            return self.username in author
        return False

    def check_if_version_lower_than_latest(self, latest_version):
        if latest_version is None:
            return  # No latest version found, possibly due to an error or new package

        current_version_tuple = tuple(map(int, self.version_number.split('.')))
        latest_version_tuple = tuple(map(int, latest_version.split('.')))

        if current_version_tuple < latest_version_tuple:
            print(f"Your version ({self.version_number}) is lower than the latest version on PyPI ({latest_version}).")
            
            if self.automatically_increment_version:
                self.version_number = self.auto_increment_version()
                return True  # Indicate that the version was incremented
            else:
                choice = self.prompt_for_input("Do you want to proceed with the lower version? Type 'yes' to proceed or enter a new version number:", input_type='text')
                if choice.lower() != 'yes':
                    self.version_number = choice  # Update the version number with user input
                    return True  # Indicate that the version was updated
                else:
                    return False  # No update to version, may need to handle differently
        else:
            print("Your version is up-to-date or higher than the version on PyPI.")
            return True  # No need for further action
    
    def verify_version_available(self):
        response = requests.get(self.api_url)
        
        if response.status_code == 200:
            data = response.json()
            versions = data['releases'].keys()  # Get all versions
            pt(versions)
            latest_version = sorted(versions, key=lambda v: tuple(map(int, v.split('.'))), reverse=True)[0]
            pt(latest_version)
            self.pypi_version_number = latest_version
            
            # Now pass the latest version to check_if_version_lower_than_latest
            self.check_if_version_lower_than_latest(latest_version)  # Check if the current version is lower and handle accordingly
            # Check if the current version is already taken
            is_version_available = self.version_number not in versions
            
            return is_version_available, self.pypi_version_number
        return False, None

    def auto_increment_version(self):
        self.verify_version_available() ## updates the self.pypi_version_number
        ## Split the version number
        parts = self.pypi_version_number.split('.')
        ## Convert the last part to an integer and increment it
        parts[-1] = str(int(parts[-1]) + 1)
        # Join the parts back into a singular version number
        self.version_number = '.'.join(parts)
        pt(self.version_number)
        return self.version_number

if __name__ == "__main__":
    verifier = PyPIVerifier(
        "A_with_nothing", 
        "developer-1v",
        "0.1.0",
        use_test_pypi=True
        )
    updated_package_name, updated_username, updated_version = verifier.handle_verification()
    pt(updated_package_name, updated_username, updated_version)