from setuptools import find_packages, setup  # type: ignore[import]

setup(
    name="setter",
    version="0.1.0",
    description="TODO",
    author="Graham Hukill",
    author_email="ghukill@gmail.com",
    url="https://github.com/ghukill/setter",
    packages=find_packages(),
    install_requires=[],
    extras_require={
        "xml": [
            "lxml>=4.9.0",
        ],
        "dataframe": [
            # TODO: iron out pandas, duckdb
        ],
    },
)
