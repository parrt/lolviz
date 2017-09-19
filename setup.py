from setuptools import setup

setup(
    name='lolviz',
    version='1.3.1',
    url='https://github.com/parrt/lolviz',
    license='BSD',
    py_modules=['lolviz'],
    author='Terence Parr',
    author_email='parrt@antlr.org',
    install_requires=['graphviz'],
    description='A simple Python data-structure visualization tool for lists of lists, lists, dictionaries',
    keywords='visualization data structures',
    classifiers=['License :: OSI Approved :: BSD License',
                 'Intended Audience :: Developers']
)
