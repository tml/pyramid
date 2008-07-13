import unittest

from zope.component.testing import PlacelessSetup

class TestMakeRegistry(unittest.TestCase, PlacelessSetup):
    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        PlacelessSetup.tearDown(self)

    def _getFUT(self):
        from repoze.bfg.registry import makeRegistry
        return makeRegistry

    def test_it(self):
        from repoze.bfg.tests import fixtureapp
        makeRegistry = self._getFUT()
        dummylock = DummyLock()
        dummyregmgr = DummyRegistrationManager()
        import repoze.bfg.registry
        try:
            old = repoze.bfg.registry.setRegistryManager(dummyregmgr)
            context, registry = makeRegistry('configure.zcml',
                                             fixtureapp,
                                             lock=dummylock)
            self.assertEqual(context.package, fixtureapp)
            from zope.component.registry import Components
            self.failUnless(isinstance(registry, Components))
            self.assertEqual(dummylock.acquired, True)
            self.assertEqual(dummylock.released, True)
            self.assertEqual(dummyregmgr.registry, registry)
        finally:
            repoze.bfg.registry.setRegistryManager(old)

class TestThreadLocalRegistryManager(unittest.TestCase, PlacelessSetup):
    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        PlacelessSetup.tearDown(self)

    def _getTargetClass(self):
        from repoze.bfg.registry import ThreadLocalRegistryManager
        return ThreadLocalRegistryManager

    def _makeOne(self):
        return self._getTargetClass()()

    def test_init(self):
        local = self._makeOne()
        from zope.component import getGlobalSiteManager
        self.assertEqual(local.registry, getGlobalSiteManager())

    def test_set_get_and_clear(self):
        local = self._makeOne()
        from zope.component import getGlobalSiteManager
        local.set(None)
        self.failIfEqual(local.registry, getGlobalSiteManager())
        self.assertEqual(local.get(), None)
        local.clear()
        self.assertEqual(local.registry, getGlobalSiteManager())

class GetSiteManagerTests(unittest.TestCase):
    def _getFUT(self):
        from repoze.bfg.registry import getSiteManager
        return getSiteManager

    def test_no_context(self):
        gsm = self._getFUT()
        from zope.component import getGlobalSiteManager
        self.assertEqual(gsm(), getGlobalSiteManager())
    
    def test_with_context(self):
        gsm = self._getFUT()
        from zope.component.interfaces import ComponentLookupError
        self.assertRaises(ComponentLookupError, gsm, object)
        
class DummyRegistrationManager:
    registry = None
    def set(self, registry):
        self.registry = registry

    def get(self):
        return self.registry

    def clear(self):
        self.cleared = True

class DummyLock:
    def acquire(self):
        self.acquired = True

    def release(self):
        self.released = True
        
