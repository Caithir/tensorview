import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="tensorview_pkg",
	version="0.0.3",
	author="Colter Norick",
	author_email="colter.norick@gmail.com",
	description="Allows viewing tensorflow data",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/Caithir/tensorview",
	packages=setuptools.find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3",
		"Operating System :: OS Independent",
	],
)
