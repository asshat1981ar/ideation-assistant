#!/usr/bin/env python3
"""
Setup script for Ideation Assistant
"""

from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="ideation-assistant",
    version="1.0.0",
    description="Advanced AI-powered development tool with DeepSeek, MCP, and GitHub integration",
    long_description=README,
    long_description_content_type="text/markdown",
    author="asshat1981ar",
    author_email="asshat1981ar@users.noreply.github.com",
    url="https://github.com/asshat1981ar/ideation-assistant",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "aiohttp>=3.8.0",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "dev": [
            "black>=22.0.0",
            "flake8>=5.0.0",
            "pytest>=7.0.0",
            "pytest-asyncio>=0.20.0",
        ],
        "full": [
            "requests>=2.28.0",
            "psutil>=5.9.0",
            "ipython>=8.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "ideation=main_interface:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Tools",
        "Topic :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    keywords="ai development planning deepseek mcp github automation",
)