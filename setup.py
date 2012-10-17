from distutils.core import setup

setup(
    name='hstore-field',
    version='1.0.0',
    description="Support for PostgreSQL's hstore for Django.",
    long_description=open('README.md').read(),
    author='Eric Russell',
    author_email='eric-r@pobox.com',
    license='BSD',
    url='http://github.com/erussell/hstore-field',
    packages=[
        'hstore_field'
    ],
)
