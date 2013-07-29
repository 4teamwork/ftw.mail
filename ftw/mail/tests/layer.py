from Products.PloneTestCase import ptc
from Testing import ZopeTestCase
import collective.testcaselayer.ptc

ptc.setupPloneSite()


class IntegrationTestLayer(collective.testcaselayer.ptc.BasePTCLayer):

    def afterSetUp(self):
        # Install the ftw.mail product
        self.addProfile('ftw.mail:default')

Layer = IntegrationTestLayer([collective.testcaselayer.ptc.ptc_layer])


class WorkspaceIntegrationTestLayer(collective.testcaselayer.ptc.BasePTCLayer):

    def afterSetUp(self):

        ZopeTestCase.installPackage('ftw.workspace')

        import ftw.workspace
        self.loadZCML('configure.zcml', package=ftw.workspace)

        self.addProfile('ftw.workspace:default')
        self.addProfile('ftw.mail:workspace')


WorkspaceLayer = WorkspaceIntegrationTestLayer(
    [collective.testcaselayer.ptc.ptc_layer])
