from setuptools import setup

setup(
    name='lolviz',
    version='1.0.1',
    url='https://github.com/parrt/lolviz',
    license='BSD',
    author='Terence Parr',
    author_email='parrt@antlr.org',
    install_requires=['graphviz'],
    description='A simple Python data-structure visualization tool for lists of lists, lists, dictionaries',
    keywords='visualization data structures',
    python_requires='<3',
    classifiers=['Programming Language :: Python :: 2.7',
                 'License :: OSI Approved :: BSD License',
                 'Intended Audience :: Developers']
)
