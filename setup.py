"""
Setup file for MCQ Database Management System
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mcq-database-manager",
    version="2.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A comprehensive MCQ Database Management System with MongoDB integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mcq-database-manager",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Topic :: Education",
        "Topic :: Database",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pymongo>=4.0.0",
        "pyperclip>=1.8.0",
    ],
    extras_require={
        "charts": ["matplotlib>=3.5.0"],
        "excel": ["pandas>=1.3.0", "openpyxl>=3.0.0"],
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
        ],
    },
    entry_points={
        "console_scripts": [
            "mcq-manager=mcq_database_manager.main:main",
        ],
    },
    package_data={
        "mcq_database_manager": ["*.json"],
    },
    include_package_data=True,
)