from pathlib import Path

from setuptools import setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="Notesh",
    version="0.8",
    description="NoteSH fully functional sticky notes App in your Terminal!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://github.com/Cvaniak/Notesh",
    author="Cvaniak",
    author_email="igna.cwaniak@gmail.com",
    packages=["notesh", "notesh/drawables", "notesh/widgets"],
    python_requires=">=3.7, <4",
    install_requires=["textual==0.37.1", "tomli==2.0.1"],
    entry_points={"console_scripts": ["notesh=notesh.command_line:run"]},
    package_data={"notesh": ["*.css", "notesh/*.css", "default_bindings.toml"]},
    data_files={"share/applications":  ["Notesh.desktop"]}.items(),
    include_package_data=True,
    zip_safe=False,
)
