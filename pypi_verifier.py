import requests
from print_tricks import pt

class PyPIVerifier:
    def __init__(self, package_name, version, owner_username):
        self.package_name = package_name
        self.version = version
        self.owner_username = owner_username
        self.api_url = f"https://pypi.org/pypi/{package_name}/json"
        self.pypi_owners = []  # New attribute to store the list of maintainers

    def verify_package_owner(self):
        response = requests.get(self.api_url)
        if response.status_code == 200:
            data = response.json()
            self.pypi_owners = [maintainer['username'] for maintainer in data['info']['maintainers']]
            return self.owner_username in self.pypi_owners
        return False

    def check_package_status(self, debug=False):
        is_new_package = self.verify_new_package()
        if is_new_package:
            is_our_package = True
            is_version_available = True
        else:
            is_our_package = self.verify_package_owner()
            is_version_available = self.verify_version_available() if is_our_package else False

        if debug:
            print(f"Debug Info: Package Available: {is_new_package}, Is Owner: {is_our_package}, Version Available: {is_version_available}")
            print(f"PyPI Owners: {self.pypi_owners}")  # Print the list of maintainers

        if is_new_package:
            message = f"Package name '{self.package_name}' is available and can be claimed."
        elif is_our_package:
            if is_version_available:
                message = f"This is an update to an existing package '{self.package_name}' that we own, and the version '{self.version}' is available."
            else:
                message = f"This is an update to an existing package '{self.package_name}' that we own, but the version '{self.version}' already exists. Please type in a different version number directly here: (or exit this, and change it in your setup/pyproject file)"
        else:
            message = f"The package name '{self.package_name}' is taken and you, '{self.owner_username}', are not the owner. The owner is '{self.pypi_owners[0]}'. Please choose a different package name here: (or exit this, and change it in your setup/pyproject file)"

        return is_new_package, is_our_package, is_version_available, message

    def verify_new_package(self):
        response = requests.get(self.api_url)
        if response.status_code == 200:
            return False  # Package name is already taken
        elif response.status_code == 404:
            return True  # Package name is available
        else:
            response.raise_for_status()

    def verify_version_available(self):
        response = requests.get(self.api_url)
        if response.status_code == 200:
            data = response.json()
            versions = data['releases'].keys()
            return self.version not in versions  # True if version is not listed
        return False

    def check_package_status(self, debug=False):
        is_new_package = self.verify_new_package()
        if is_new_package:
            is_our_package = True
            is_version_available = True
        else:
            is_our_package = self.verify_package_owner()
            is_version_available = self.verify_version_available() if is_our_package else False

        if debug:
            print(f"Debug Info: Package Available: {is_new_package}, Is Owner: {is_our_package}, Version Available: {is_version_available}")

        if is_new_package:
            message = f"Package name '{self.package_name}' is available and can be claimed."
        elif is_our_package:
            if is_version_available:
                message = f"This is an update to an existing package '{self.package_name}' that we own, and the version '{self.version}' is available."
            else:
                message = f"This is an update to an existing package '{self.package_name}' that we own, but the version '{self.version}' already exists. Please type in a different version number directly here: (or exit this, and change it in your setup/pyproject file)"
        else:
            message = f"The package name '{self.package_name}' is taken and you, '{self.owner_username}', are not the owner. Please choose a different package name here: (or exit this, and change it in your setup/pyproject file)"

        return is_new_package, is_our_package, is_version_available, message


if __name__ == "__main__":
    verifier = PyPIVerifier(
        "test_package_for_builds", 
        "1.0.0", 
        "your_username"
        )
    status = verifier.check_package_status(
        debug=True
        )
    pt(status)