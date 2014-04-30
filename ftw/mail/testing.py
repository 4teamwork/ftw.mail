from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from ftw.mail.tests import builders
from plone.app.testing import FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.testing import z2
from zope.configuration import xmlconfig


class FtwMailLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        import z3c.autoinclude
        xmlconfig.file('meta.zcml', z3c.autoinclude,
                       context=configurationContext)
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <includePlugins package="plone" />'
            '</configure>',
            context=configurationContext)

        import ftw.mail
        xmlconfig.file('configure.zcml', ftw.mail,
                       context=configurationContext)

        z2.installProduct(app, 'ftw.workspace')
        import ftw.workspace
        xmlconfig.file('configure.zcml', ftw.workspace,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.mail:default')
        applyProfile(portal, 'ftw.workspace:default')


FTW_MAIL_LAYER = FtwMailLayer()
FTW_MAIL_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FTW_MAIL_LAYER,
           set_builder_session_factory(functional_session_factory)),
    name="ftw.mail:functional")
