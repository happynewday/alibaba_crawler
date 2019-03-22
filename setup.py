#!/usr/bin/env python
#coding=utf8

try:
    from  setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

setup(
        name = 'alibaba_crawler',
        version = '1.0',
        install_requires = ['requests', 'lxml', 'mysqlclient'], 
        description = 'alibaba crawler',
        url = 'https://github.com/zhouxianggen/alibaba_crawler.git', 
        author = 'zhouxianggen',
        author_email = 'zhouxianggen@gmail.com',
        classifiers = [ 'Programming Language :: Python :: 3.7',],
        packages = ['alibaba_crawler'],
        data_files = [ 
                ('/conf/supervisor/program/', ['alibaba_crawler.ini']),], 
        entry_points = { 'console_scripts': [
                'run_alibaba_crawler = alibaba_crawler.run:main', ]}   
        )

