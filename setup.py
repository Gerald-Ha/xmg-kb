# ------------------------------------------------------------------------------
# XMG-KB - RGB Keyboard Controller
# Version: 2.1.1
# Author: Gerald Hasani
# Email: contact@gerald-hasani.com
# GitHub: https://github.com/Gerald-Ha
# ------------------------------------------------------------------------------

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='xmg-kb',
    version='2.1.1',
    description='XMG Keyboard - RGB Controller für ITE 8291 Tastaturen',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Gerald Hasani',
    author_email='contact@gerald-hasani.com',
    url='https://github.com/Gerald-Ha/xmg-kb',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'xmg-kb = xmg.main:main',
        ]
    },
    install_requires=[
        'pyusb',
        'elevate'
    ],
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Topic :: System :: Hardware',
    ],
)
