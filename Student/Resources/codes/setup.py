import io
import os
import os.path as op

from setuptools import PEP420PackageFinder  # isort: skip
from distutils.core import setup  # isort: skip


ROOT = op.dirname(op.abspath(__file__))
SRC = op.join(ROOT, "src")


def get_install_req():
    with io.open("deploy/requirements.txt") as fh:
        install_reqs = fh.read()
    install_reqs = [l for l in install_reqs.split("\n") if len(l) > 1]
    return install_reqs


install_reqs = get_install_req()


setup(
    name="rag_ai_studio",
    version="0.0.1",
    package_dir={"": "src"},
    description="DS Innovation - NLP",
    author="Tiger Analytics",
    packages=PEP420PackageFinder.find(where=str(SRC)),
    python_requires=">=3.10.13",
    install_requires=install_reqs,
)
