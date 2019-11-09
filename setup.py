import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="music-metadata-territories",
    version="19a1.dev2",
    author="Matija Kolarić",
    author_email="matijakolaric@users.noreply.github.com",
    description="Music Metedata - Territory-related tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/musicmetadata/territories",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)