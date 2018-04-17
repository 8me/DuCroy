#!/usr/bin/env python

import unittest
from unittest.mock import patch
from ducroy.osci_control import Osci


class TestOsci(unittest.TestCase):
    @patch('visa.ResourceManager')
    def test_init(self, rm):
        osci = Osci('1')
        rm.assert_called_with("@py")
