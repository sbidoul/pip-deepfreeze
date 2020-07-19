import pathlib

from setuptools import setup

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.rst").read_text(encoding="utf-8")

setup(
    name="pip-deepfreeze",
    use_scm_version=True,
    description="A simple pip freeze workflow for Python application developers.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/sbidoul/pip-deepfreeze",
    author="Stéphane Bidoul",
    author_email="stephane.bidoul@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    package_dir={"": "src"},
    packages=["pip_deepfreeze"],
    python_requires=">=3.6",
    install_requires=[
        "httpx",
        'importlib_resources ; python_version<"3.9"',
        "packaging",
        "typer[all]",
        'typing-extensions ; python_version<"3.8"',  # for Protocol
    ],
    extras_require={
        "test": ["pytest", "pytest-cov", "pytest-xdist", "virtualenv"],
        "mypy": ["mypy"],
    },
    entry_points={
        "console_scripts": [
            "pip-df=pip_deepfreeze.__main__:main",
            "pip-deepfreeze=pip_deepfreeze.__main__:main",
        ]
    },
    project_urls={
        "Bug Reports": "https://github.com/sbidoul/pip-deepfreeze/issues",
        "Source": "https://github.com/sbidoul/pip-deepfreeze/",
        "Changelog": (
            "https://github.com/sbidoul/pip-deepfreeze/blob/master/HISTORY.rst"
        ),
    },
)
