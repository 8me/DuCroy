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

    @patch('visa.ResourceManager')
    def test_write(self, rm_mock):
        ip = '1'
        osci = Osci(ip)
        osci.visa_if = MagicMock()
        osci.write("VDIV","C1","1","V")
        osci.visa_if.write.assert_called_with("C1:VDIV 1V")

    @patch('visa.ResourceManager')
    def test_read(self, rm_mock):
        ip = '1'
        osci = Osci(ip)
        osci.visa_if = MagicMock()
        osci.read("VDIV","C1")
        osci.visa_if.query.assert_called_with("C1:VDIV?")

    def test_variable_conversion(self):
        ip = '1'
        osci = Osci(ip)
        self.assertEqual(osci.decimal_to_visa_string(1e3),"1.00E+03")
