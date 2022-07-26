from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in field_force/__init__.py
from field_force import __version__ as version

setup(
	name="field_force",
	version=version,
	description="Field Force App",
	author="Invento Software Limited",
	author_email="fieldforce@invento.com.bd",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
