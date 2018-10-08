import unittest
import os
import sys
import shutil
import string
from optparse import OptionParser
import logging


sys.dont_write_bytecode = True

import coshsh
from coshsh.generator import Generator
from coshsh.datasource import Datasource
from coshsh.application import Application
from coshsh.configparser import CoshshConfigParser
from coshsh.util import setup_logging

class CoshshTest(unittest.TestCase):
    def print_header(self):
        print "#" * 80 + "\n" + "#" + " " * 78 + "#"
        print "#" + string.center(self.id(), 78) + "#"
        print "#" + " " * 78 + "#\n" + "#" * 80 + "\n"

    def setUp(self):
        self.config = coshsh.configparser.CoshshConfigParser()
        self.config.read('etc/coshsh.cfg')
        self.generator = coshsh.generator.Generator()
        setup_logging()

    def tearDown(self):
        #shutil.rmtree("./var/objects/testsnmptt", True)
        #shutil.rmtree("./etc/check_logfiles/snmptt", True)
        pass

    def test_create_recipe_multiple_sources(self):
        self.print_header()
        self.generator.add_recipe(name='testsnmptt', **dict(self.config.items('recipe_TESTsnmptt')))
        self.config.set("datasource_CSVunity", "name", "unity")
        cfg = self.config.items("datasource_CSVunity")
        self.generator.recipes['testsnmptt'].add_datasource(**dict(cfg))
        self.config.set("datasource_snmptt", "name", "snmptt")
        cfg = self.config.items("datasource_snmptt")
        self.generator.recipes['testsnmptt'].add_datasource(**dict(cfg))
        recipe = self.generator.recipes['testsnmptt']
        #recipe.add_datarecipient(**dict([('type', 'datarecipient_coshsh_default'), ('name', 'datarecipient_coshsh_default'), ('objects_dir', recipe.objects_dir), ('max_delta', recipe.max_delta), ('max_delta_action', recipe.max_delta_action), ('safe_output', recipe.safe_output)]))
        self.config.set("datarecipient_checklogfiles_mibs", "name", "checklogfiles_mibs")
        cfg = self.config.items("datarecipient_checklogfiles_mibs")
        self.generator.recipes['testsnmptt'].add_datarecipient(**dict(cfg))

        # remove target dir / create empty
        self.generator.recipes['testsnmptt'].count_before_objects()
        self.generator.recipes['testsnmptt'].cleanup_target_dir()

        self.generator.recipes['testsnmptt'].prepare_target_dir()
        # check target

        # read the datasources
        self.generator.recipes['testsnmptt'].collect()
        self.generator.recipes['testsnmptt'].assemble()

        # for each host, application get the corresponding template files
        # get the template files and cache them in a struct owned by the recipe
        # resolve the templates and attach the result as config_files to host/app
        self.generator.recipes['testsnmptt'].render()
        self.assert_(hasattr(self.generator.recipes['testsnmptt'].objects['hosts']['test_host_0'], 'config_files'))
        self.assert_('host.cfg' in self.generator.recipes['testsnmptt'].objects['hosts']['test_host_0'].config_files['nagios'])

        # write hosts/apps to the filesystem
        self.generator.recipes['testsnmptt'].output()
        self.assert_(os.path.exists("var/objects/testsnmptt/dynamic/hosts"))
        self.assert_(os.path.exists("var/objects/testsnmptt/dynamic/hosts/test_host_0"))
        self.assert_(os.path.exists("var/objects/testsnmptt/dynamic/hosts/test_host_0/os_unity_traps.cfg"))
        self.assert_(os.path.exists("var/objects/testsnmptt/dynamic/hosts/test_host_1/os_unity_traps.cfg"))
        os_unity_traps_cfg = open("var/objects/testsnmptt/dynamic/hosts/test_host_1/os_unity_traps.cfg").read()
        self.assert_('.1.3.6.1.4.1.1139.103.1.18.2.2' in os_unity_traps_cfg)
        self.assert_('.1.3.6.1.4.1.1139.103.1.18.2.3' in os_unity_traps_cfg)
        print self.generator.recipes['testsnmptt'].objects["applications"]["test_host_1+os+unity"].type
        print self.generator.recipes['testsnmptt'].objects["applications"]["test_host_1+os+unity"].version


if __name__ == '__main__':
    unittest.main()


