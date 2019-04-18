#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

# Get version from version.py file
with open("akeneo/version.py", "r") as fd:
    exec(fd.read())  # import __version__

setup(
    name="akeneo",
    version=__version__,  # noqa
    description="A Python wrapper for the Akeneo REST API",
    long_description=open("README.rst").read(),
    author="Auguria",
    url="https://github.com/AuguriaTeam/python-akeneo",
    license="LICENSE",
    packages=find_packages(),
    include_package_data=True,
    platforms=["any"],
    install_requires=[
        "requests_toolbelt",
        "requests",
        "urllib3",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
)
