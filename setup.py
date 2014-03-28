from setuptools import setup, find_packages
import os

version = '2.1.0'

tests_require = [
    'ftw.builder',
    'ftw.workspace',
    'plone.app.testing',
    ]

setup(name='ftw.mail',
      version=version,
      description='Provides a mail content type and a mail-in behavior',
      long_description=open('README.rst').read() + '\n' + \
          open(os.path.join('docs', 'HISTORY.txt')).read(),

      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.1',
        'Framework :: Plone :: 4.2',
        'Framework :: Plone :: 4.3',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

      keywords='',
      author='4teamwork GmbH',
      author_email='mailto:info@4teamwork.ch',
      url='https://github.com/4teamwork/ftw.mail',
      license='GPL2',

      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw'],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
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
        'ftw.upgrade',
        ],

      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      entry_points='''
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      ''',
      )
