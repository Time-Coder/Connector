import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tcp-connector",
    version="0.0.7",
    author="Time-Coder",
    author_email="binghui.wang@foxmail.com",
    description="A lightweight network programming tool for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Time-Coder/Glass-Engine",
    packages=setuptools.find_packages(),
    install_requires=[
        "dill",
        "netifaces"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)