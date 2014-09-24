import sys
sys.path.insert(0, 'src')
from ibmiotc import __version__

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='ibmiotc',
    version=__version__,
    author='David Parker',
    author_email='parkerda@uk.ibm.com',
    package_dir={'': 'src'},
    packages=['ibmiotc'],
    url='https://github.com/ibm-messaging/iot-python',
    license=open('LICENSE').read(),
    description='IBM Internet of Things Cloud for Python',
	long_description=open('README.txt').read(),
    install_requires=[
        "paho-mqtt >= 1.0",
        "iso8601 >= 0.1.10",
    ]
)