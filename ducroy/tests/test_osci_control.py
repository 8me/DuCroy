#!/usr/bin/env python

import unittest
from unittest.mock import patch, MagicMock
from ducroy.osci_control import Osci, OPEN_CMD


class TestOsci(unittest.TestCase):
    @patch('visa.ResourceManager')
    def test_init(self, rm_mock):
        osci = Osci('1')  # noqa
        rm_mock.assert_called_with("@py")

    @patch('visa.ResourceManager')
    def test_open_resource(self, rm_mock):
        ip = '1'
        osci = Osci(ip)
        osci.rm = MagicMock()
        osci._open_resource()
        osci.rm.open_resource.assert_called_with(OPEN_CMD.format(ip))
