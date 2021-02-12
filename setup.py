from setuptools import setup

setup(
    name='worcomal',
    version='0.1',
    description='Modeling compositional word formation across languages',
    url='http://github.com/wswu/worcomal',
    author='Winston Wu',
    author_email='wswu@jhu.edu',
    license='MIT',
    packages=['worcomal'],
    install_requires=['tqdm', 'numpy', 'scipy'],
    zip_safe=False)