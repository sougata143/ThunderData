from setuptools import setup, find_packages

setup(
    name="thunderdata",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.1.1",
        "numpy>=1.24.3",
        "pyspark>=3.5.0",
        "sqlalchemy>=2.0.22",
        "python-dotenv>=1.0.0",
    ],
)
