from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="iqdb-api",
    version="1.0.0",
    author="hieuxyz",
    author_email="khongbt446@gmail.com",
    description="Thư viện Python để tìm kiếm hình ảnh ngược trên IQDB.org.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hieuxyz00/iqdb-api-python",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "types-beautifulsoup4",
            "types-Pillow",
        ],
    },
    keywords="iqdb reverse image search anime manga cosplay",
    project_urls={
        "Bug Reports": "https://github.com/hieuxyz00/iqdb-api-python/issues",
        "Source": "https://github.com/hieuxyz00/iqdb-api-python",
    },
)