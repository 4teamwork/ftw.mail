from Products.PloneTestCase import ptc
import collective.testcaselayer.ptc

ptc.setupPloneSite()


class IntegrationTestLayer(collective.testcaselayer.ptc.BasePTCLayer):

    def afterSetUp(self):
        # Install the ftw.mail product
        self.addProfile('plone.app.intid:default')
        self.addProfile('ftw.mail:default')

Layer = IntegrationTestLayer([collective.testcaselayer.ptc.ptc_layer])
