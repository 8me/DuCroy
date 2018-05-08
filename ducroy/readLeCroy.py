from struct import unpack
import numpy as np
import struct


def read_timetrace(filename, N):
    '''
    Read binary waveform file (.trc) from LeCroy waverunner
    Based on Matlab file LCREAD.m
    Input:
        filename : filename, string
    Output:

    '''

    fid = open(filename, "rb")
    data = fid.read(50).decode('ascii')
    WAVEDESC = str.find(data, 'WAVEDESC')

    aCOMM_TYPE = WAVEDESC + 32
    aCOMM_ORDER = WAVEDESC + 34
    aWAVE_DESCRIPTOR = WAVEDESC + 36  # length of the descriptor block
    aUSER_TEXT = WAVEDESC + 40  # length of the usertext block
    aTRIGTIME_ARRAY = WAVEDESC + 48  # length of the TRIGTIME array
    aWAVE_ARRAY_1 = WAVEDESC + 60  # length (in Byte) of the sample array

    aRESERVED1 = WAVEDESC + 112
    # aRESERVED2 = WAVEDESC + 114
    # number of datapoints in data array
    # (should be == WAVE_ARRAY_1 for "byte" style)
    aWAVE_ARRAY_COUNT = WAVEDESC + 116
    # (real?) number of sequences (= subarrays)
    aSUBARRAY_COUNT = WAVEDESC + 144

    aVERTICAL_GAIN = WAVEDESC + 156
    aVERTICAL_OFFSET = WAVEDESC + 160

    # nominal number of sequences (= subarrays)
    aNOM_SUBARRAY_COUNT = WAVEDESC + 174

    aHORIZ_INTERVAL = WAVEDESC + 176
    aHORIZ_OFFSET = WAVEDESC + 180

    # determine the number storage format
    # HIFIRST / LOFIRST    (big endian / little endian)

    fid.seek(aCOMM_ORDER)
    COMM_ORDER = ord(fid.read(1))
    # print("aCOMM_ORDER: {}".format(aCOMM_ORDER))
    # print("COMM_ORDER: {}".format(COMM_ORDER))
    if COMM_ORDER == 0:
        fmt = '>'
    else:
        fmt = '<'
    # print("fmt: {}".format(fmt))
    COMM_TYPE = ReadWord(fid, fmt, aCOMM_TYPE)
    print("COMM_TYPE: {}".format(COMM_TYPE))
    WAVE_DESCRIPTOR = ReadLong(fid, fmt, aWAVE_DESCRIPTOR)
    print("WAVE_DESCRIPTOR: {}".format(WAVE_DESCRIPTOR))
    USER_TEXT = ReadLong(fid, fmt, aUSER_TEXT)
    print("USER_TEXT: {}".format(USER_TEXT))
    TRIGTIME_array = ReadLong(fid, fmt, aTRIGTIME_ARRAY)
    print("TRIGTIME_array: {}".format(TRIGTIME_array))
    WAVE_ARRAY_1 = ReadLong(fid, fmt, aWAVE_ARRAY_1)
    print("WAVE_ARRAY_1: {}".format(WAVE_ARRAY_1))
    SUBARRAY_COUNT = ReadLong(fid, fmt, aSUBARRAY_COUNT)
    print("SUBARRAY_COUNT: {}".format(SUBARRAY_COUNT))
    VERTICAL_GAIN = ReadFloat(fid, fmt, aVERTICAL_GAIN)
    print("VERTICAL_GAIN: {}".format(VERTICAL_GAIN))
    try:
        VERTICAL_OFFSET = ReadFloat(fid, fmt, aVERTICAL_OFFSET)
    except:  # noqa
        # print("No vertical offset found in: {}".format(filename))
        VERTICAL_OFFSET = np.nan
    # print("VERTICAL_OFFSET: {}".format(VERTICAL_OFFSET))
    NOM_SUBARRAY_COUNT = ReadWord(fid, fmt, aNOM_SUBARRAY_COUNT)
    # print("NOM_SUBARRAY_COUNT: {}".format(NOM_SUBARRAY_COUNT))
    if NOM_SUBARRAY_COUNT == 0:
        res1 = ReadWord(fid, fmt, aRESERVED1)
        res2 = ReadWord(fid, fmt, aRESERVED1)
        WAVE_ARRAY_COUNT = ReadLong(fid, fmt, aWAVE_ARRAY_COUNT)
        print("Wave_ARRAY_COUNT: {}".format(WAVE_ARRAY_COUNT))
        SUBARRAY_COUNT = res1 * res2   # TOTAL number of sequences
        WAVE_ARRAY_1 = WAVE_ARRAY_COUNT  # TOTAL number of datapoints
    HORIZ_INTERVAL = ReadFloat(fid, fmt, aHORIZ_INTERVAL)
    HORIZ_OFFSET = ReadDouble(fid, fmt, aHORIZ_OFFSET)
    fid.close()
    # print(data, WAVEDESC, COMM_ORDER, COMM_TYPE, WAVE_DESCRIPTOR,
    # USER_TEXT, TRIGTIME_array, WAVE_ARRAY_1)
    fid = open(filename, "rb")
    y = np.array([])
    for i in range(N):
        y1 = ReadData(fid, fmt,
                      WAVEDESC + WAVE_DESCRIPTOR + USER_TEXT + TRIGTIME_array +
                      i * WAVE_ARRAY_1, WAVE_ARRAY_1)   # voltage [counts]

        y = np.append(y, y1)
    x = np.arange(1, len(y) + 1)  # *HORIZ_INTERVAL + HORIZ_OFFSET
    fid.close()

    return (x.reshape(SUBARRAY_COUNT * N, WAVE_ARRAY_1 // SUBARRAY_COUNT),
            y.reshape(SUBARRAY_COUNT * N, WAVE_ARRAY_1 // SUBARRAY_COUNT),
            VERTICAL_GAIN,
            VERTICAL_OFFSET,
            HORIZ_INTERVAL,
            HORIZ_OFFSET)


def ReadByte(fid, fmt, Addr):
    fid.seek(Addr)
    s = fid.readline(1)
    s = unpack(fmt + 'b', s)
    if(type(s) == tuple):
        return s[0]
    else:
        return s


def ReadWord(fid, fmt, Addr):
    fid.seek(Addr)
    s = fid.readline(2)
    s = unpack(fmt + 'h', s)
    if(type(s) == tuple):
        return s[0]
    else:
        return s


def ReadLong(fid, fmt, Addr):
    fid.seek(Addr)
    s = fid.readline(4)
    s = unpack(fmt + 'l', s)
    if(type(s) == tuple):
        return s[0]
    else:
        return s


def ReadFloat(fid, fmt, Addr):
    fid.seek(Addr)
    s = fid.readline(4)
    s = unpack(fmt + 'f', s)
    if(type(s) == tuple):
        return s[0]
    else:
        return s


def ReadDouble(fid, fmt, Addr):
    fid.seek(Addr)
    s = fid.readline(8)
    s = unpack(fmt + 'd', s)
    if(type(s) == tuple):
        return s[0]
    else:
        return s


def ReadData(fid, fmt, Addr, datalen):
    fid.seek(Addr)
    fmt = fmt + str(datalen) + "b"
    nbytes = struct.calcsize(fmt)
    data = fid.read(nbytes)
    result = np.frombuffer(data, 'b', nbytes)
    return result
