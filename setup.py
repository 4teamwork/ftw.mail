from setuptools import find_packages
from setuptools import setup
import os


version = '2.7.3'

tests_require = [
    'ftw.builder',
    'ftw.testbrowser',
    'ftw.workspace',
    'ftw.zipexport',
    'plone.app.testing',
    'unittest2',
    ]

setup(name='ftw.mail',
      version=version,
      description='Provides a mail content type and a mail-in behavior',
      long_description=open('README.rst').read() + '\n' + \
          open(os.path.join('docs', 'HISTORY.txt')).read(),

      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.3',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

      keywords='',
      author='4teamwork AG',
      author_email='mailto:info@4teamwork.ch',
      url='https://github.com/4teamwork/ftw.mail',
      license='GPL2',

      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw'],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
        'plone.api',
        'plone.app.referenceablebehavior',
        'plone.registry',
        'plone.dexterity',
        'setuptools',
        'BeautifulSoup!=4.0b',
        'plone.app.dexterity',
        'plone.app.registry',
        'plone.namedfile[blobs]',
        'collective.autopermission',
        'collective.dexteritytextindexer',
        'plone.directives.form',
        'ftw.upgrade >= 1.11.0',
        'premailer < 3.7.0',
        ],

      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      entry_points='''
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      ''',
      )
