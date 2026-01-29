#!/usr/bin/env python3
"""Setup script for Creator Content Monitor."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text() if readme_path.exists() else ""

setup(
    name="creator-monitor",
    version="1.0.0",
    description="Monitor content creators and predict their responses to your questions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    python_requires=">=3.8",
    py_modules=["content_monitor", "creator_api"],
    install_requires=[],
    extras_require={
        "rss": ["feedparser>=6.0.0", "requests>=2.28.0"],
        "api": ["flask>=2.0.0"],
        "all": ["feedparser>=6.0.0", "requests>=2.28.0", "flask>=2.0.0"],
    },
    entry_points={
        "console_scripts": [
            "creator-monitor=content_monitor:main",
            "ask-creators=content_monitor:quick_ask",
        ],
    },
    package_data={
        "": ["creators.json"],
    },
    data_files=[("", ["creators.json"])],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
