import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

REQUIRES = [
    "requests",
]

setuptools.setup(
    name="Gardena-python",
    version="0.0.1",
    author="Andreas Hartl",
    author_email="gardena-python@nd-com.net",
    description="A Python API for the Gardena Smart System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nd-net/Gardena-python",
    python_requires=">=3.5",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Home Automation",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
