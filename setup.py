from setuptools import setup, find_packages

exec(open('samsung_mdc/version.py').read())

requires = [
    'click',  # tested: click >=7,<=8
    'jinja2',
    'pyserial-asyncio'  # tested: pyserial==3.5; pyserial-asyncio==0.5
]

setup(
    name='python-samsung-mdc',
    version=__version__,  # noqa
    description=('Samsung Multiple Display Control (MDC) '
                 'protocol implementation (asyncio library + CLI interface)'),
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='BSD',
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Telecommunications Industry',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'Topic :: Multimedia :: Video :: Display',
        'Topic :: Home Automation',
        'Topic :: Utilities',
    ],
    python_requires='>=3.7,<4.0',
    author='Victor Gavro',
    author_email='vgavro@gmail.com',
    url='http://github.com/vgavro/samsung-mdc',
    keywords=['samsung', 'mdc'],
    packages=find_packages(),
    install_requires=requires,
    entry_points={
        'console_scripts': [
            'samsung-mdc=samsung_mdc.cli:cli',
        ],
    }
)
