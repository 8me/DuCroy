"""
Binary data parser for LeCroy waverunner.

"""
from struct import unpack
import numpy as np


def read_timetrace(filename):
    '''
    Read binary waveform file (.trc) from LeCroy waverunner
    Based on Matlab file LCREAD.m

    Parameters
    ----------
    filename : str

    Returns
    -------
    x, y, v_gain, v_off, h_int, h_off

    '''
    fid = open(filename, "rb")
    data = fid.read(50).decode('ascii')
    offset = str.find(data, 'WAVEDESC')
    fid.seek(offset + 32, 0)

    COMM_TYPE = unpack('<h', fid.read(2))  # noqa
    fmt = '>' if ord(fid.read(1)) == 0 else '<'  # endianness
    fid.read(1)
    wave_descriptor = unpack(fmt + 'l', fid.read(4))[0]
    data = unpack(fmt + '6l', fid.read(6*4))
    user_text, _, trigtime_array, _, _, wave_array_1 = data
    fid.read(48)
    res1, res2, wave_array_count = unpack(fmt + 'hhl', fid.read(8))
    fid.read(24)
    subarray_count, _, _, v_gain, v_off = unpack(fmt + '3lff', fid.read(5*4))
    fid.read(10)
    nom_subarray_count, h_int, h_off = unpack(fmt + 'hfd', fid.read(2+4+8))

    if nom_subarray_count == 0:
        subarray_count = res1 * res2
        wave_array_1 = wave_array_count  # TOTAL number of datapoints

    fid.seek(offset + wave_descriptor + user_text + trigtime_array, 0)
    y = np.frombuffer(fid.read(wave_array_1), 'b', wave_array_1)
    x = np.arange(1, len(y) + 1)  # *h_int + h_off

    fid.close()

    return (x.reshape(subarray_count, wave_array_1 // subarray_count),
            y.reshape(subarray_count, wave_array_1 // subarray_count),
            v_gain, v_off, h_int, h_off)
