from peerscout.preprocessing.updateDataAndReload import (
    MODULE_NAMES,
    load_modules
)


class TestLoadModules:
    def test_should_be_able_to_load_all_modules(self):
        assert MODULE_NAMES
        modules = list(load_modules(MODULE_NAMES))
        assert len(modules) == len(MODULE_NAMES)
