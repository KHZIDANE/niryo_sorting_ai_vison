from setuptools import find_packages
from setuptools import setup

setup(
    name='niryo_interfaces',
    version='0.1.0',
    packages=find_packages(
        include=('niryo_interfaces', 'niryo_interfaces.*')),
)
