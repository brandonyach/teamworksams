from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="teamworksams",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.2.3",
        "requests",
        "requests_toolbelt",
        "python-dotenv",
        "tqdm",
    ],
    extras_require={"test": ["pytest>=7.0", "pytest-cov>=4.0", "pytest-vcr", "responses>=0.23"]},
    author="Brandon Yach",
    author_email="yachb35@gmail.com",
    description="A Python library for interacting with the Teamworks AMS API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/brandonyach/teamworksams",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)