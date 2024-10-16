# *****************************************************************************
# Copyright (c) 2014, 2024 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import sys
import os
sys.path.insert(0, 'src')

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if not os.path.exists('README.rst'):
    import pypandoc
    pypandoc.download_pandoc(targetfolder='~/bin/')
    pypandoc.convert_file('README.md', 'rst', outputfile='README.rst')

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='wiotp-sdk',
    version="1.0.1",
    author='David Parker',
    author_email='parkerda@uk.ibm.com',
    package_dir={'': 'src'},
    packages=[
        'wiotp.sdk',
        'wiotp.sdk.device',
        'wiotp.sdk.gateway',
        'wiotp.sdk.application',
        'wiotp.sdk.api',
        'wiotp.sdk.api.dsc',
        'wiotp.sdk.api.registry',
        'wiotp.sdk.api.mgmt',
        'wiotp.sdk.api.status',
        'wiotp.sdk.api.usage',
        'wiotp.sdk.api.lec',
        'wiotp.sdk.api.services',
        'wiotp.sdk.api.actions',
        'wiotp.sdk.api.state'
    ],
    namespace_packages=['wiotp'],
    package_data={'wiotp.sdk': ['*.pem']},
    scripts=[
        'bin/wiotp-cli'
    ],
    url='https://github.com/ibm-watson-iot/iot-python',
    license="Eclipse Public License - v1.0",
    description='Python SDK for Maximo IoT and IBM Watson IoT Platform',
    long_description=long_description,
    install_requires=[
        "iso8601 >= 0.1.12",
        "pytz >= 2020.1",
        "pyyaml >= 5.3.1",
        "paho-mqtt >= 1.5.0, < 2.0.0",
        "requests >= 2.23.0",
        "requests_toolbelt >= 0.9.1",
    ],
    extras_require={
        'dev': [
            'build',
            'pytest'
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Communications',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
