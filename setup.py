import sys
sys.path.insert(0, 'src')

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='ibmiotf',
    version="0.3.0",
    author='David Parker',
    author_email='parkerda@uk.ibm.com',
    package_dir={'': 'src'},
    packages=['ibmiotf', 'ibmiotf.codecs'],
    package_data={'ibmiotf': ['*.pem']},
    url='https://github.com/ibm-watson-iot/iot-python',
    license=open('LICENSE').read(),
    description='Python Client for IBM Watson IoT Platform',
    long_description=open('README.rst').read(),
    install_requires=[
        "iso8601 >= 0.1.10",
        "paho-mqtt >= 1.2",
        "pytz >= 2014.7",
        "requests >= 2.5.0",
        "requests_toolbelt >= 0.7.0",
        "dicttoxml >= 1.7.4",
        "xmltodict >= 0.10.2"
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
