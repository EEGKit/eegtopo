from setuptools import setup, find_packages

setup(
    name="eegtopo",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "matplotlib>=3.3.0",
        "pandas>=1.3.0",
        "mne>=1.0.0",
    ],
    python_requires=">=3.8",
    author="Ido Haber",
    author_email="idochaber@gmail.com",
    description="EEG Topographic Analysis Package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/idossha/eegtopo",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
