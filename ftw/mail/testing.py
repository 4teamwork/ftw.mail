from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from ftw.mail.tests import builders  # noqa
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2
from zope.configuration import xmlconfig


class FtwMailLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '</configure>',
            context=configurationContext,
        )

        import Products.CMFPlacefulWorkflow
        xmlconfig.file('configure.zcml', Products.CMFPlacefulWorkflow, context=configurationContext)

        try:
            # Plone >= 4.3.x
            import Products.DataGridField
            xmlconfig.file('configure.zcml', Products.DataGridField, context=configurationContext)
        except:
            pass

        z2.installProduct(app, 'ftw.file')
        z2.installProduct(app, 'ftw.meeting')
        z2.installProduct(app, 'ftw.workspace')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.mail:default')
        applyProfile(portal, 'ftw.workspace:default')
        applyProfile(portal, 'ftw.zipexport:default')


FTW_MAIL_LAYER = FtwMailLayer()
FTW_MAIL_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FTW_MAIL_LAYER, set_builder_session_factory(functional_session_factory)),
    name="ftw.mail:functional",
)
