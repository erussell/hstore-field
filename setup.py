from setuptools import setup

setup(
    name='hstore-field',
    version='1.0.6',
    description="Support for PostgreSQL's hstore for Django.",
    long_description=open('README.rst').read(),
    author='Eric Russell, Anant Asthana',
    author_email='erussell@pobox.com,anant.asty@gmail.com',
    url='http://github.com/anantasty/hstore-field',
    packages=['hstore_field'],
    include_package_data=True,
    license='BSD',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
)
