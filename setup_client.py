from setuptools import setup

setup(
    name='stemlab_client',
    version='1.0',
    packages=['stemlab_client', 'stemlab_client.common', 'stemlab_client.sensors'],
    url='',
    license='Apache 2.0',
    author='Carl Wilen',
    author_email='dawgwaredev@gmail.com',
    description='An example REST API client for polling sensor data and reporting back to central server.',
    entry_points={
        'console_scripts': [
            'sensor_client = stemlab_client.sensor_client:launch'
        ],
    },
    install_requires=['arrow',
                      'requests',
                      'futures',
                      'path.py',
                      'collection-json']
)
