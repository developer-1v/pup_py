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

    def prompt_for_input(self, prompt_message, input_type='text'):
        """
        Generic method to prompt user for input. Adapts to GUI or CLI based on configuration.
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
            ## CLI input
            return input(prompt_message)

    def auto_increment_version(self):
        ## Split the version number
        parts = self.version_number.split('.')
        ## Convert the last part to an integer and increment it
        parts[-1] = str(int(parts[-1]) + 1)
        # Join the parts back into a singular version number
        self.version_number = '.'.join(parts)
        pt(self.version_version)
        return self.version_number

    def handle_verification(self):
        is_new_package, is_our_package, is_version_available, message = self.check_package_status()
        print(message)

        if not is_our_package:
            choice = self.prompt_for_input("Package name might be taken or username might be incorrect. Choose an option:\n1. Change package name\n2. Change username\nEnter choice (1 or 2):", input_type='choice')
            if choice == '1':
                new_package_name = self.prompt_for_input("Enter a new package name:")
                if new_package_name:
                    self.package_name = new_package_name
                    return self.handle_verification()
            elif choice == '2':
                new_username = self.prompt_for_input("Enter a new username:")
                if new_username:
                    self.username = new_username
                    return self.handle_verification()

        if not is_version_available:
            if self.automatically_increment_version:
                self.auto_increment_version()
                return self.handle_verification()
            else:
                new_version = self.prompt_for_input("Enter a new version number:")
                if new_version:
                    self.version_number = new_version
                    return self.handle_verification()

        return self.package_name, self.username, self.version_number

    def check_package_status(self, debug=True):
        is_new_package = self.verify_new_package()
        if is_new_package:
            is_our_package = True
            is_version_available = True
        else:
            is_our_package = self.verify_package_owner()
            is_version_available = self.verify_version_available() if is_our_package else False

        if debug:
            pt(is_new_package, 
                is_our_package, 
                self.username, 
                self.pypi_owners, 
                is_version_available, 
                self.version_number
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
            pt(data)
            # pt.ex()
            # Safely access the 'maintainers' key using get() to avoid KeyError
            maintainers = data['info'].get('maintainers', [])
            self.pypi_owners = [maintainer['username'] for maintainer in maintainers]
            return self.username in self.pypi_owners
        return False

    def verify_version_available(self):
        response = requests.get(self.api_url)
        if response.status_code == 200:
            data = response.json()
            versions = data['releases'].keys()
            return self.version_number not in versions 
        return False



if __name__ == "__main__":
    verifier = PyPIVerifier(
        "A_with_nothing", 
        "developer-1v",
        "0.1.0",
        use_test_pypi=False
        )
    updated_package_name, updated_username, updated_version = verifier.handle_verification()
    pt(updated_package_name, updated_username, updated_version)