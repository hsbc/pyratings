from setuptools import find_packages, setup

file = None
try:
    file = open("README.rst", "r")
    long_description = file.read()
finally:
    if file is not None:
        file.close()

setup(
    name="pyratings",
    version="0.5.2",
    author="Andreas Vester",
    author_email="andreas.vester@hsbc.de",
    description=(
        "Collection of functions in order to translate ratings "
        "from various rating agencies into equivalent rating scores and vice versa."
    ),
    long_description=long_description,
    long_description_content_type="text/x-rst",
    license="Apache License Version 2.0",
    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={"pyratings": ["resources/*.*"]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Office/Business :: Financial",
        "Topic :: Office/Business :: Financial :: Accounting",
        "Topic :: Office/Business :: Financial :: Investment",
        "Typing :: Typed",
    ],
    python_requires=">=3.9",
    install_requires=[
        "numpy",
        "pandas",
    ],
    extras_require={
        "dev": [
            "black",
            "deprecation",
            "jupyter",
            "nbsphinx",
            "numpydoc",
            "openpyxl",  # used for sphinx
            "pandoc",  # used for sphinx, install via conda
            "pytest",
            "pytest-cov",
            "sphinx",
            "sphinx-rtd-theme",
            "tox",
        ],
    },
)
