from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="liriklagu-otomatis",
    version="1.0.0",
    author="Your Name",
    author_email="renzaja11@gmail.com",
    description="A tool to automatically generate and display lyrics from audio files in real-time",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JangkrikMc/liriklagu_otomatis",
    packages=find_packages(include=['src']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "liriklagu=src.main:main",
        ],
    },
    package_data={
        "": ["*.md", "*.txt"],
    },
    include_package_data=True,
)