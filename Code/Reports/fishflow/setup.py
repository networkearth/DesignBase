import setuptools

setuptools.setup(
    name="fishflow",
    version="0.1.0",
    packages=["fishflow", "fishflow.common", "fishflow.depth"],
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "h3>=4.0.0",
        "pyarrow>=6.0.0",
        "geojson>=2.5.0",
    ],
    python_requires=">=3.9",
    author="FishFlow Team",
    description="A python package for generating reports for the FishFlow app",
    long_description="FishFlow is a package for generating fish depth distribution reports using Bayesian model interpolation.",
)
