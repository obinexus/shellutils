#!/usr/bin/env python3
"""
OBINexus Shellutils Setup
=========================
Installation package for OBINexus integrated shellutils module

Features:
- NexusSearch AVL trie with witness pattern
- Platform-aware file duplication
- Document archiving and indexing
- Actor model event bubbling
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="obinexus-shellutils",
    version="1.0.0",
    author="OBINexus Computing",
    author_email="obinexus@example.com",
    description="Integrated shellutils for OBINexus framework with NexusSearch and file management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/obinexus/shellutils",
    packages=find_packages(),
    py_modules=[
        "pheno_nexus_search",
        "file_archiver",
        "obinexus_shellutils"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Filesystems",
        "Topic :: Text Processing :: Indexing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies - uses only standard library
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "obinexus-shellutils=obinexus_shellutils:main",
            "nexus-search=pheno_nexus_search:main",
            "nexus-archive=file_archiver:main",
        ],
    },
    scripts=[
        "shellutils.sh",
    ],
    include_package_data=True,
    package_data={
        "": ["*.sh", "*.md"],
    },
    keywords=[
        "obinexus",
        "nexus-search",
        "avl-trie",
        "file-archiving",
        "witness-pattern",
        "actor-model",
        "document-indexing",
        "state-machine",
        "pheno-token",
    ],
    project_urls={
        "Bug Reports": "https://github.com/obinexus/shellutils/issues",
        "Source": "https://github.com/obinexus/shellutils",
        "Documentation": "https://github.com/obinexus/shellutils/wiki",
    },
)
