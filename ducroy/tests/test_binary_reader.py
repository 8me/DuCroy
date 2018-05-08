import os
import tempfile
import unittest

from ducroy.readLeCroy import read_timetrace

CWD = os.path.join(os.path.dirname(__file__), 'test_data')
TESTFILENAME = os.path.join(CWD, "test.trc")



class TestBinaryReader(unittest.TestCase):
    def test_call_with_invalid_filename(self):
        with self.assertRaises(FileNotFoundError):
            read_timetrace('foo', 1)

    def test_call_with_valid_filename(self):
        f = tempfile.NamedTemporaryFile(delete=True)
        with self.assertRaises(TypeError):
            read_timetrace(f.name, 1)
        f.close()

    def test_call_with_valid_data(self):
        read_timetrace(TESTFILENAME, 1)
        
