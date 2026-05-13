from setuptools import find_packages, setup

package_name = 'smart_lighting_controller'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools', 'paho-mqtt'],
    zip_safe=True,
    maintainer='eileen',
    maintainer_email='eileenteoh10399@gmail.com',
    description='Scheduled MQTT lighting controller for NTU dorm rooms',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'lighting_controller = smart_lighting_controller.lighting_controller:main',
        ],
    },
)
