import requests

class PyPIVerifier:
    def __init__(self, package_name):
        self.package_name = package_name
        self.api_url = f"https://pypi.org/pypi/{package_name}/json"

    def is_package_available(self):
        """ Check if the package name is available on PyPI. """
        response = requests.get(self.api_url)
        if response.status_code == 200:
            return False  # Package name is already taken
        elif response.status_code == 404:
            return True  # Package name is available
        else:
            response.raise_for_status()

    def verify_package_owner(self, owner_username):
        """ Verify if the specified username is an owner of the package. """
        response = requests.get(self.api_url)
        if response.status_code == 200:
            data = response.json()
            owners = [maintainer['username'] for maintainer in data['info']['maintainers']]
            return owner_username in owners
        return False

if __name__ == "__main__":
    verifier = PyPIVerifier("test_package_for_builds")
    print("Is available:", verifier.is_package_available())
    print("Is owner:", verifier.verify_package_owner("your_username"))

