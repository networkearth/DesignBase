"""Setup script for fishflow reports package."""

from setuptools import setup, find_packages

setup(
    name="fishflow",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "h3>=4.0.0",
        "pyarrow>=6.0.0",
        "geojson>=2.5.0",
    ],
    python_requires=">=3.9",
    author="FishFlow Team",
    description="Generate depth occupancy reports for FishFlow analysis",
    long_description=open("README.md").read() if __name__ == "__main__" else "",
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
