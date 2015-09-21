from setuptools import setup

setup(
    name='sumologic',
    version='0.0.1',
    author='Mihir Singh (@citruspi)',
    author_email='hello@mihirsingh.com',
    description='A Python client for Sumo Logic',
    url='https://github.com/citruspi/py-sumologic',
    classifiers=[
        'License :: Public Domain',
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
        'Operating System :: Unix',
        'Operating System :: MacOS :: MacOS X',
    ],
    packages=['sumologic'],
    zip_safe=False,
    include_package_date=True,
    platforms='any'
)
