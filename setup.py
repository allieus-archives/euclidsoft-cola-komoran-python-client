from setuptools import setup, find_packages

setup_requires = [
]

install_requires = [
    'ray',
    'grpcio',
    'tqdm',
]

dependency_links = [
    'https://github.com/lovit/textrank/archive/master.zip',
]
 
setup(
    name='cola-komoran-python-client',
    version='1.2.2',
    url='https://github.com/euclidsoft/cola-komoran-python-client',
    author='Chinseok Lee',
    author_email='me@askcompany.kr',
    description='Python Client for cola-komoran',
    packages=find_packages(exclude=['tests']),
    long_description=open('README.md', encoding="utf8").read(),
    zip_safe=False,
    setup_requires=setup_requires,
    install_requires=install_requires,
    dependency_links=dependency_links,
)

