import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from codecs import open

with open('shareplum/version.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

setup(
    name='SharePlum',
    version=version,
    description='Python SharePoint Library',
    long_description=open('README.rst').read(),
    url='https://github.com/jasonrollins/shareplum',
    author='Jason Rollins',
    author_email='jason.c.rollins@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Office/Business',
    ],
    keywords=['SharePoint'],
    packages=['shareplum'],
    install_requires=['lxml', 'requests', 'requests-ntlm'],
)
