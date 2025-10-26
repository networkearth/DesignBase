"""
Setup script for the fishflow package.
"""

from setuptools import setup, find_packages

setup(
    name='fishflow',
    version='0.1.0',
    description='FishFlow depth report generation package',
    author='FishFlow Team',
    author_email='info@fishflow.com',
    packages=find_packages(),
    install_requires=[
        'numpy>=1.20.0',
        'pandas>=1.3.0',
        'h3>=3.7.0',
        'pyarrow>=6.0.0',
        'geojson>=2.5.0',
    ],
    python_requires='>=3.9',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
