import sys
sys.path.insert(0, 'src')

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='ibmiotf',
    version="0.0.10",
    author='David Parker',
    author_email='parkerda@uk.ibm.com',
    package_dir={'': 'src'},
    packages=['ibmiotf'],
    package_data={'ibmiotf': ['*.pem']},
    url='https://github.com/ibm-messaging/iot-python',
    license=open('LICENSE').read(),
    description='IBM Internet of Things Foundation for Python',
	long_description=open('README.txt').read(),
    install_requires=[
        "iso8601 >= 0.1.10",
        "paho-mqtt >= 1.0",
		"pytz >= 2014.7",
		"requests >= 2.5.0"
    ]
)