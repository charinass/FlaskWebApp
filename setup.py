from setuptools import setup

setup(
    name='ttn-app',
    packages=['Application'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)