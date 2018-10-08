import unittest
import os
import sys
import shutil
import string
from optparse import OptionParser
import ConfigParser
import logging
import subprocess


sys.dont_write_bytecode = True

import coshsh
from coshsh.generator import Generator
from coshsh.util import setup_logging

class CoshshTest(unittest.TestCase):
    def print_header(self):
        print "#" * 80 + "\n" + "#" + " " * 78 + "#"
        print "#" + string.center(self.id(), 78) + "#"
        print "#" + " " * 78 + "#\n" + "#" * 80 + "\n"

    def setUp(self):
        shutil.rmtree("./var/objects/test16", True)
        os.makedirs("./var/objects/test16")
        self.config = ConfigParser.ConfigParser()
        self.config.read('etc/coshsh.cfg')
        self.generator = coshsh.generator.Generator()
        setup_logging()

    def tearDown(self):
        #shutil.rmtree("./var/objects/test16", True)
        pass 


    def test_pushgateway(self):
        self.print_header()
        self.assert_(os.path.exists("../bin/coshsh-cook"))
        subprocess.call("../bin/coshsh-cook --cookbook etc/coshsh.cfg --recipe PUSH", shell=True)
        self.assert_(os.path.exists("var/objects/test16/dynamic"))

    def test_pushgateway2(self):
        self.print_header()
        import time
        time.sleep(19)
        subprocess.call("../bin/coshsh-cook --cookbook etc/coshsh.cfg --recipe PUSH2", shell=True)
        self.assert_(os.path.exists("var/objects/test16/dynamic"))


if __name__ == '__main__':
    unittest.main()


