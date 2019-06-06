#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    "argh==0.26.2",
    "certifi==2019.3.9",
    "chardet==3.0.4",
    "distconfig==0.1.0",
    "future==0.17.1",
    "googleapis-common-protos==1.5.10",
    "grpcio==1.20.1",
    "idna==2.8",
    "logzero==1.5.0",
    "numpy==1.16.3",
    "opencv-python>=4.1.0.25",
    "pathlib==1.0.1",
    "pathtools==0.1.2",
    "prometheus-client==0.6.0",
    "protobuf==3.7.1",
    "protoc-gen-swagger==0.1.0",
    "python-consul==1.1.0",
    "pytoml==0.1.20",
    "PyYAML==5.1",
    "requests==2.22.0",
    "scipy==1.3.0",
    "six==1.12.0",
    "ujson==1.35",
    "urllib3==1.25.2",
    "videt-dar-tools>=0.1.2",
    "videt-grpc-interceptor>=0.1.0",
    "videt-idl>=0.9.0",
    "videt-protos>=2.0.1",
    "videt-py-conf>=1.0.0",
    "vyper-config==0.3.3",
    "watchdog==0.9.0"
]

setup_requirements = []

test_requirements = []

setup(
    author="zhangxuanrui",
    author_email='xuanrui.zhang@videt.cn',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    description="dar sg customs netapp invoice grpc",
    entry_points={
        'console_scripts': [
            "videt-dar-sg-customs-pcg-packinglist-grpc=v_dar_sg_customs_pcg_packinglist_grpc.main:run",
        ],
    },
    install_requires=requirements,
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords="videt-dar-sg-customs-pcg-packinglist-grpc",
    name="videt-dar-sg-customs-pcg-packinglist-grpc",
    packages=find_packages(include=["v_dar_sg_customs_pcg_packinglist_grpc", "v_dar_sg_customs_pcg_packinglist_grpc.*"]),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url="https://git.videt.cn/zxrtt/videt-dar-sg-customs-pcg-packinglist-grpc",
    version='0.1.0',
    zip_safe=False,
)
