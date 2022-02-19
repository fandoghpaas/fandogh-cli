from distutils.core import setup

import setuptools

from fandogh_cli import VERSION

setup(
    name='fandogh_cli',
    packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
    version=VERSION,
    description='Official CLI for Fandogh PaaS',
    author='Soroosh Sarabadani',
    install_requires=["click>=7.0",
                      "retrying",
                      "pyOpenSSL",
                      "requests[security]",
                      "requests-toolbelt",
                      "beautifultable==0.8.0",
                      "pytz",
                      "tzlocal==2.1",
                      "pyyaml==5.4.1",
                      "websocket-client"],
    author_email='soroosh.sarabadani@gmail.com',
    url='https://github.com/fandoghpaas/fandogh-cli',
    keywords=['PaaS', 'Fandogh'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    entry_points='''
        [console_scripts]
        fandogh=fandogh_cli.fandogh:base
    ''',

)
