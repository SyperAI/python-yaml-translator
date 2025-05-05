from setuptools import setup, find_packages

setup(
    name='YAML Translator',
    version='1.2.0',
    packages=find_packages(),
    install_requires=['PyYAML==6.0.2'],
    author='StarMan',
    description='Class for working with translations based on YAML files.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/SyperAI/python-yaml-translator',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ]
)