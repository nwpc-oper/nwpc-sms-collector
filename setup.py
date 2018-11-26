from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='nwpc-sms-collector',

    version='0.2.0',

    description='An SMS collector at NWPC.',
    long_description=long_description,

    url='https://github.com/perillaroc/nwpc-system-collector',

    author='perillaroc',
    author_email='perillaroc@gmail.com',

    license='MIT',

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6'
    ],

    keywords='nwpc SMS collector',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    install_requires=[
        'click',
        'requests',
        'nwpc_workflow_model'
    ],

    extras_require={
        'grpc': ['grpcio', 'googleapis-common-protos']
    },

    entry_points={}
)
