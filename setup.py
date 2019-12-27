from setuptools import setup, find_packages
from os import path


def read_requirements(filename):
    file = '%s/%s' % (path.dirname(path.realpath(__file__)), filename)
    with open(file) as f:
        return [line.strip() for line in f]

packages = find_packages()
# Ensure that we don't pollute the global namespace.
for p in packages:
    assert p == 'hashtag_monitor' or p.startswith('hashtag_monitor.')

setup(
    name='Hashtag-Monitor',
    version="0.0.1",
    author='lccasagrande',
    license="MIT",
    package_dir={'hashtag_monitor': 'hashtag_monitor'},
    packages=packages,
    install_requires=read_requirements('requirements.txt'),
    python_requires='>=3.7',
    scripts=['scripts/manage.py']
)