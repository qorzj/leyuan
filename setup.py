# coding: utf-8
"""
leyuan
~~~~~~~~

Leyuan is a consul based cluster management tool.

Setup
-----

.. code-block:: bash

    > pip install leyuan

Links
-----
* `README <https://github.com/qorzj/leyuan>`_

"""

from setuptools import setup
from os import path
from setuptools.command.install import install

here = path.abspath(path.dirname(__file__))


class MyInstall(install):
    def run(self):
        print("-- installing... (powered by lesscli) --")
        install.run(self)


setup(
        name = 'leyuan',
        version='1.1.1',
        description='Leyuan Cluster Tool',
        long_description=__doc__,
        url='https://github.com/qorzj/leyuan',
        author='qorzj',
        author_email='inull@qq.com',
        license='MIT',
        platforms=['any'],

        classifiers=[
            ],
        keywords='lesscli',
        packages = ['leyuan', 'leyuan.daemon_lib'],
        install_requires=['lesscli', 'requests', 'docker'],

        cmdclass={'install': MyInstall},
        entry_points={
            'console_scripts': [
                'ly = leyuan.index:main',
                ],
            },
    )
