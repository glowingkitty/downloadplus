import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="downloadplus",
    version="1.0.0",
    author="Marco",
    author_email=None,
    description="A download manager that takes urls, json files as well as Notion as an input and can download files from an URL as well as via torrent.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/glowingkitty/downloadplus",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=["notion"]
)
