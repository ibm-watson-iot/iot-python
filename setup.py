# *****************************************************************************
# Copyright (c) 2014, 2018 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import sys
sys.path.insert(0, 'src')

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# =============================================================================
# Convert README.md to README.rst for pypi
# Need to install both pypandoc and pandoc 
# - pip insall pypandoc
# - https://pandoc.org/installing.html
# =============================================================================
try:
    from pypandoc import convert

    def read_md(f):
        return convert(f, 'rst')
except:
    print('Warning: pypandoc module not found, unable to convert README.md to RST')
    print('Unless you are packaging this module for distribution you can ignore this error')

    def read_md(f):
        return "Python SDK for IBM Watson IoT Platform"

setup(
    name='wiotp-sdk',
    version="0.12.0",
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
    license=open('LICENSE').read(),
    description='Python SDK for IBM Watson IoT Platform',
    long_description=read_md('README.md'),
    install_requires=[
        "iso8601 >= 0.1.12",
        "pytz >= 2020.1",
        "pyyaml >= 5.3.1",
        "paho-mqtt >= 1.5.0",
        "requests >= 2.23.0",
        "requests_toolbelt >= 0.9.1",
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Communications',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
