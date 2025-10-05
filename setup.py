from setuptools import find_packages,setup
from typing import List

HYPHEN_DOT_E = "-e ."
def get_requirements(file_path):
    with open(file_path) as requirements:
        lines = requirements.readlines()
        requirements = [
            req.strip() for req in lines
            if req.strip() and req.strip() != "-e ."  
        ]
    return requirements


setup(
    name = "PERSONALIZED_OFFERS_PROJECT",
    version = "0.0.1",
    author = "Lakshman",
    author_email = "lakshman102999@gmail.com",
    packages = find_packages(),
    install_requires  = get_requirements("requirements.txt")

)