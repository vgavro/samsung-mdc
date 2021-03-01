from setuptools import setup, find_packages, Extension

requires = [
    'click',
]

setup(
    name='samsung-mdc',
    version='0.0.1',
    description='http://github.com/vgavro/samsung-mdc',
    long_description='http://github.com/vgavro/samsung-mdc',
    license='BSD',
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
    ],
    author='Victor Gavro',
    author_email='vgavro@gmail.com',
    url='http://github.com/vgavro/samsung-mdc',
    keywords='',
    packages=find_packages(),
    install_requires=requires,
    entry_points={
        'console_scripts': [
            'samsung-mdc=samsung_mdc.cli:cli',
        ],
    }
)
