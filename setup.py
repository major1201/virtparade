# encoding: utf-8

from setuptools import find_packages, setup


setup(
    name='virtparade',
    version='0.1.1',
    python_requires='>=3.4',
    url='https://github.com/major1201/virtparade',
    author='major1201',
    author_email='major1201@gmail.com',
    description='An easy-use tool help you create kvm virtual machines gracefully with simple configuration on Linux servers.',
    license='private',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Jinja2',
        'MarkupSafe',
        'PyYAML',
        'six',
    ],
    scripts=[
        'bin/virtparade',
    ],
    extras_require={},
    classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    ],
)
