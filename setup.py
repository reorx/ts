#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages


package_name = 'ts'


def get_version():
    import ast

    """Return version string."""
    with open(package_name + '/__init__.py') as input_file:
        for line in input_file:
            if line.startswith('__version__'):
                return ast.parse(line).body[0].value.s


def get_requires():
    try:
        with open('requirements.txt', 'r') as f:
            requires = [i for i in map(lambda x: x.strip(), f.readlines()) if i]
        return requires
    except IOError:
        return []


def get_long_description():
    try:
        with open('README.md', 'r') as f:
            return f.read()
    except IOError:
        return ''


setup(
    # license='License :: OSI Approved :: MIT License',
    name=package_name,
    version=get_version(),
    author='reorx',
    author_email='novoreorx@gmail.com',
    description='Twitter Search CLI',
    url='https://github.com/reorx/ts',
    long_description=get_long_description(),
    # Or use (make sure find_packages is imported from setuptools):
    packages=find_packages(),
    # Or if it's a single file package
    #py_modules=['project_sketch'],
    install_requires=get_requires(),
    # package_data={}
    entry_points={
        'console_scripts': ['ts = ts.core:main']
    }
)
