from setuptools import setup, find_packages

setup(
    name='growth-targeting',
    version='0.0.1',
    description='',
    author='Emanuele Moscato',
    author_email='emanuele.m@asidatascience.com',
    packages=find_packages(),
    install_requires=[
        'tweepy',
        'daiquiri',
        'dash',
        'dash_html_components',
        'dash_core_components'
    ], #external packages as dependencies
)
