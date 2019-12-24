from setuptools import setup, find_packages
from os import path


def read_requirements(filename):
    file = '%s/%s' % (path.dirname(path.realpath(__file__)), filename)
    with open(file) as f:
        return [line.strip() for line in f]

setup(
    name='Hashtag-Monitor',
    version="0.0.1",
    author='lccasagrande',
    package_dir={'hashtag_monitor': 'hashtag_monitor'},
    packages=find_packages(),
    install_requires=read_requirements('requirements.txt'),
    python_requires='>=3.7',
    scripts=['scripts/manage.py']
)