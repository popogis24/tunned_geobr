from setuptools import setup, find_packages

setup(
    name="tunned_geobr",
    version="0.1.0",
    author="Anderson Stolfi",
    author_email="",  # Adicione seu email se desejar
    description="Fork personalizado do geobr com funcionalidades extras para download de dados geográficos brasileiros",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/popogis24/tunned_geobr",
    packages=["tunned_geobr"],
    install_requires=[
        "geopandas>=0.9.0",
        "pandas>=1.0.0",
        "requests>=2.0.0",
        "fiona>=1.8.0",
        "shapely>=1.7.0",
        "gdown>=4.5.1",  # For Google Drive downloads
        "tabulate>=0.8.9",  # For formatted table output
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: GIS",
    ],
    python_requires=">=3.6",
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=21.5b2",
            "flake8>=3.9.2",
        ],
    },
    project_urls={
        "Bug Tracker": "https://github.com/popogis24/tunned_geobr/issues",
        "Documentation": "https://github.com/popogis24/tunned_geobr",
        "Source Code": "https://github.com/popogis24/tunned_geobr",
    },
)
