from setuptools import setup, find_packages
import os

version = open('ftw/mail/version.txt').read().strip()
maintainer = 'Thomas Buchberger'

tests_require = []

setup(name='ftw.mail',
      version=version,
      description="Provides a mail content type and a mail-in behavior" + \
          ' (Maintainer: %s)' % maintainer,
      long_description=open("README.txt").read() + "\n" + \
          open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='%s, 4teamwork GmbH' % maintainer,
      author_email='mailto:info@4teamwork.ch',
      url='http://psc.4teamwork.ch/4teamwork/ftw/ftw.mail/',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'BeautifulSoup',
        'Plone',
        'plone.app.dexterity',
        'plone.app.registry',
        'plone.namedfile',
        'collective.autopermission',
        'collective.testcaselayer',
        # -*- Extra requirements: -*-
        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
