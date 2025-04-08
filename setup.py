from setuptools import setup, find_packages

setup(
    name="godbrain",
    version="0.1.0",
    description="Advanced modular AI architecture with symbolic reasoning and meta-awareness",
    author="GODBRAIN Team",
    author_email="sololevelingsofi@gmail.com",
    packages=find_packages(where="src"),
    package_dir={"":"src"},
    python_requires=">=3.8",
    install_requires=[
        "numpy",
        "pandas",
        "scipy",
        "jupyter",
        "notebook",
        "ipywidgets",
        "pyswip",
        "networkx",
        "pyvis",
        "torch",
        "transformers",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)