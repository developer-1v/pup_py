'''
NOTE:
    Development Status:
        1 - Planning
        2 - Pre-Alpha
        3 - Alpha
        4 - Beta
        5 - Production/Stable
        6 - Mature
        7 - Inactive

'''
import subprocess
from setuptools import setup, find_packages
from utilities import *



def setup_package():
    """Setup the package with provided metadata and files."""
    readme = read_file('README.md')
    history = read_file('HISTORY.md')
    requirements = generate_requirements()

    setup(
        author="Developer 1v",
        author_email='Developer-1v@proton.me',
        python_requires='>=3.6',
        classifiers=[
            'Development Status :: 2 - Pre-Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Natural Language :: English',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.6', ## Minimal Supported Version
            'Programming Language :: Python :: 3.11', ## Latest Tested Version
        ],
        description="""Creates a package from a source and then automatically 
                    tests the package, uploads to PyPI, and installs to your PC""",
        entry_points={
            'console_scripts': [
                'pup_py=pup_py.cli:main',
            ],
        },
        install_requires=requirements,
        license="MIT license",
        long_description=readme + '\n\n' + history,
        include_package_data=True,
        keywords=['pup_py', 'pup', 'puppy', 'Pip Universal Projects', 'automated pip'],
        name='pup_py',
        packages=find_packages(include=['pup_py', 'pup_py.*']),
        test_suite='tests',
        tests_require=['pytest>=3'],
        url='https://github.com/developer-1v/pup_py',
        project_urls={
            'Documentation': 'https://pup_py.readthedocs.io',
            'Source': 'https://github.com/developer-1v/pup_py',
            'Tracker': 'https://github.com/developer-1v/pup_py/issues',
            'PyPI': 'https://pypi.org/project/pup_py/'
        },
        version='0.1.0',
        zip_safe=False,
    )

if __name__ == '__main__':
    setup_package()
