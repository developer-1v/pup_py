import requests

class PyPIVerifier:
    def __init__(self, package_name):
        self.package_name = package_name
        self.api_url = f"https://pypi.org/pypi/{package_name}/json"

    def is_package_available(self):
        response = requests.get(self.api_url)
        if response.status_code == 200:
            return False  # Package name is already taken
        elif response.status_code == 404:
            return True  # Package name is available
        else:
            response.raise_for_status()

    def verify_package_owner(self, owner_username):
        response = requests.get(self.api_url)
        if response.status_code == 200:
            data = response.json()
            owners = [maintainer['username'] for maintainer in data['info']['maintainers']]
            return owner_username in owners
        return False

    def check_package_status(self, owner_username):
        available = self.is_package_available()
        if available:
            return (True, True, "This is a first-time upload for a new package & we can claim the package name.")
        else:
            is_owner = self.verify_package_owner(owner_username)
            if is_owner:
                return (False, True, "This is an update to an existing package that we own.")
            else:
                return (False, False, "The package name is taken and you are not the owner. Please choose a different package name.")

if __name__ == "__main__":
    verifier = PyPIVerifier("test_package_for_builds")
    print("Is available:", verifier.is_package_available())
    print("Is owner:", verifier.verify_package_owner("your_username"))

