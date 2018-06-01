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
        return "Python Client for IBM Watson IoT Platform"

setup(
    name='ibmiotf',
    version="0.3.5",
    author='David Parker',
    author_email='parkerda@uk.ibm.com',
    package_dir={'': 'src'},
    packages=[
        'ibmiotf', 
        'ibmiotf.api',
        'ibmiotf.api.registry',
        'ibmiotf.codecs'
    ],
    package_data={'ibmiotf': ['*.pem']},
    url='https://github.com/ibm-watson-iot/iot-python',
    license=open('LICENSE').read(),
    description='Python Client for IBM Watson IoT Platform',
    long_description=read_md('README.md'),
    install_requires=[
        "iso8601 >= 0.1.12",
        "paho-mqtt >= 1.3.1",
        "pytz >= 2017.3",
        "requests >= 2.18.4",
        "requests_toolbelt >= 0.8.0",
        "dicttoxml >= 1.7.4",
        "xmltodict >= 0.11.0"
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Communications',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
