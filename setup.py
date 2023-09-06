from setuptools import find_packages, setup  # type: ignore[import]

setup(
    name="steamboat",
    version="0.1.0",
    description="DAG oriented data pipeline task orchestrator",
    author="Graham Hukill",
    author_email="ghukill@gmail.com",
    url="https://github.com/ghukill/steamboat",
    packages=find_packages(),
    install_requires=[],
    extras_require={
        "xml": [
            "lxml>=4.9.0",
        ],
        "dataframe": [
            "duckdb==0.8.1",
            "pandas==2.0.3",
        ],
    },
)
