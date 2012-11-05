from setuptools import setup

setup(
    name='hstore-field',
    version='1.0.1',
    description="Support for PostgreSQL's hstore for Django.",
    long_description=open('README.md').read(),
    author='Eric Russell',
    author_email='eric-r@pobox.com',
    url='http://github.com/erussell/hstore-field',
    packages=['hstore_field'],
    include_package_data=True,
    license='BSD',
)
