import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="music_metadata_territories",
    version="24.12",
    author="Matija Kolarić",
    author_email="matijakolaric@users.noreply.github.com",
    description="Music Metedata - Territory-related tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://matijakolaric.com/development/musicmetadata/",
    project_urls={
        'Created by': 'https://matijakolaric.com',
        'Code Repository': 'https://github.com/musicmetadata/territories',
    },
    packages=setuptools.find_namespace_packages(include=['music_metadata.*']),
    namespace_packages=['music_metadata'],
    package_data={
        '': ['*.csv'],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires='>=3.11',
)
