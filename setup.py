try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from codecs import open

setup(
    name='SharePlum',
    version='0.1.0',
    description='Python SharePoint Library',
    long_description=open('README.rst').read(),
    url='',
    author='Jason Rollins',
    author_email='jason.c.rollins@gmail.com',
    license='LICENSE.txt',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Office/Business',
    ],
    keywords='MicroSoft SharePoint SharePoint2010 SharePoint2013',
    packages=['shareplum'],
    install_requires=['lxml', 'requests'],
)
