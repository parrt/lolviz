from setuptools import setup

setup(
    name='lolviz',
    version='1.4.3',
    url='https://github.com/parrt/lolviz',
    license='BSD',
    py_modules=['lolviz'],
    author='Terence Parr',
    author_email='parrt@antlr.org',
    install_requires=['graphviz'], # needs numpy if you use ndarrayviz()
    description='A simple Python data-structure visualization tool for call stacks, lists of lists, lists, dictionaries, numpy arrays',
    keywords='visualization data structures',
    classifiers=['License :: OSI Approved :: BSD License',
                 'Intended Audience :: Developers']
)
