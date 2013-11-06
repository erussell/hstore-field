from setuptools import setup

setup(
    name='hstore-field',
    version='1.0.3',
    description="Support for PostgreSQL's hstore for Django.",
    long_description=open('README.md').read(),
    author='Eric Russell, Anant Asthana',
    author_email='eric-r@pobox.com,anant.asty@gmail.com',
    url='http://github.com/anantasty/hstore-field',
    packages=['hstore_field'],
    include_package_data=True,
    license='BSD',
)
