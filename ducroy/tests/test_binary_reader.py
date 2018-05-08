import os
import tempfile
import unittest

import numpy as np

from ducroy.binary_reader import read_timetrace

CWD = os.path.join(os.path.dirname(__file__), 'test_data')
TESTFILENAME = os.path.join(CWD, "test.trc")


class TestBinaryReader(unittest.TestCase):
    def test_call_with_invalid_filename(self):
        with self.assertRaises(FileNotFoundError):
            read_timetrace('foo')

    def test_call_with_valid_data(self):
        read_timetrace(TESTFILENAME)

    def test_output(self):
        x, y, v_gain, v_off, h_int, h_off = read_timetrace(TESTFILENAME)
        self.assertAlmostEqual(0.00884, v_gain, 5)
        self.assertAlmostEqual(0.61, v_off, 5)
        self.assertAlmostEqual(2e-10, h_int, 11)
        self.assertAlmostEqual(1.35e-7, h_off, 8)

    def test_output_x(self):
        x, y, v_gain, v_off, h_int, h_off = read_timetrace(TESTFILENAME)
        assert 500 == len(x)
        assert np.allclose([1, 2, 3, 4, 5, 6, 7], x[0, :7])
        assert np.allclose([1003, 1004, 1005, 1006, 1007], x[1, :5])
        assert np.allclose([101, 102], x[0, 100:102])
        assert np.allclose([51, 52], x[0, 50:52])

    def test_output_y(self):
        x, y, v_gain, v_off, h_int, h_off = read_timetrace(TESTFILENAME)
        assert 500 == len(y)
        assert np.allclose([70., 69., 68., 70., 70., 70., 71.], y[0, :7])
        assert np.allclose([71., 71., 70., 71., 71., 71., 69.], y[1, :7])
        assert np.allclose([68., 70.], y[0, 200:202])
        assert np.allclose([68., 69.], y[0, 140:142])
