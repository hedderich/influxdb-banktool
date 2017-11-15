from setuptools import setup

setup(
    name='influxdb-banktool',
    version='0.1.0',

    license='Apache-2.0',
    url='https://github.com/hedderich/influxdb-banktool',
    author='Marvin Hedderich',
    author_email='dev@hedderich.info',
    description='Extract FinTS account balances and load them into influxdb',

    packages=['influxdb_banktool'],
    install_requires=['fints', 'influxdb'],

    entry_points={
        'console_scripts': ['influxdb-banktool=influxdb_banktool.main:main'],
    }
)
