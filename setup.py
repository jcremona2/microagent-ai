from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="microagent",
    version="0.1.0",
    author="Julian Cremona",
    author_email="jncremona@gmail.com",
    description="A micro agent framework for building AI agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jcremona2/microagent-ai",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Add your project's dependencies here
        # e.g., 'requests>=2.25.1',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'black',
            'flake8',
        ],
    },
)
