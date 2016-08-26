#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages


# Use semantic versioning: MAJOR.MINOR.PATCH
version = '0.1.0'


def get_long_description():
    try:
        with open('README.md', 'r') as f:
            return f.read()
    except IOError:
        return ''


setup(
    # license='License :: OSI Approved :: MIT License',
    name='ts',
    version=version,
    author='reorx',
    author_email='novoreorx@gmail.com',
    description='Twitter Search CLI',
    url='https://github.com/reorx/ts',
    long_description=get_long_description(),
    # Or use (make sure find_packages is imported from setuptools):
    packages=find_packages(),
    # Or if it's a single file package
    #py_modules=['project_sketch'],
    install_requires=[
        'oauth2',
        'requests',
        'arrow',
        'fabulous',
        'requests_oauthlib',
    ],
    # package_data={}
    entry_points={
        'console_scripts': ['ts = ts.core:main']
    }
)
