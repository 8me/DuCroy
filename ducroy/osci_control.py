#!/usr/bin/env python

import visa

OPEN_CMD = "TCPIP0::{}::INSTR"


class Osci(object):

    def __init__(self, ip):
        self.ip = ip
        self.rm = visa.ResourceManager('@py')
        self.visa_if = None

    def _open_resource(self):
        self.visa_if = self.rm.open_resource(OPEN_CMD.format(self.ip))

    def write(self, command, channel=None, value=None, unit=None):
        if channel is not None:
            command = channel + ":" + command
        if value is not None:
            command = command + " " + value
        if unit is not None:
            command = command + unit
        try:
            self.visa_if.write(command)
        except:
            print("Invalid combination of commands!")

    def read(self, command, channel=None):
        if channel is not None:
            command = channel + ":" + command
        command = command + "?"
        try:
            return self.visa_if.query(command)
        except:
            print("Couldn't read command!")
            return None

    def set_channel_vdiv(self, voltage, channel):
        command = "VDIV"
        voltage_string = self.decimal_to_visa_string(voltage)
        self.write(command, channel, voltage_string, "V")
        retval = self.get_channel_gain(channel)
        return retval

    def get_channel_vdiv(self, channel):
        command = "VDIV"
        readback = self.read(command,channel)
        readback = readback.replace(channel+":"+command,"")
        readback = readback.replace("V","")
        return float(readback)

    def get_channel_gain(self, channel):
        command = channel + ":INSP? \"VERTICAL_GAIN\""
        readback = self.visa_if.query(command)
        readback = readback.replace("\"","")
        readback = readback.replace(channel+":INSP","")
        readback = readback.replace(":","")
        readback = readback.replace("VERTICAL_GAIN","")
        return float(readback)

    def set_timebase(self, timebase):
        """Writes the timebase setting of the oscilloscope
        Parameters
        ----------
        timebase: the timebase, which should be written to the osci
        Returns
        -------
        timebase: readback of the timebase [seconds/div]
        """
        command = "TDIV"
        timebase_string = self.decimal_to_visa_string(timebase)
        self.write(command, value=timebase_string)
        return self.get_timebase()


    def get_timebase(self):
        """Reads the current timebase setting of the oscilloscope
        Returns
        -------
        timebase: timebase float [seconds/div]
        """
        command = "TDIV"
        readback = self.read(command)
        readback = readback.replace(command,"")
        readback = readback.replace("S","")
        return float(readback)

    def get_horizontal_interval(self):
        """Reads the current horizontal interval (meaning the timestep between
        two samples) setting of the oscilloscope
        Returns
        -------
        timebase: timebase float [seconds/div]
        """
        command = "INSP? \"HORIZ_INTERVAL\""
        readback = self.visa_if.query(command)
        readback = readback.split('"')[1]
        readback = readback.replace("HORIZ_INTERVAL","")
        readback = readback.replace(":","")
        return float(readback)

    def set_holdoff(self, events):
        command = "TRSE"
        trigger_settings = self._read_trigger_select()



    def _read_trigger_select(self):
        command = "TRSE"
        readback = self.read(command)
        readback = self._clean_string(readback)
        values = readback.split(",")
        type = values[0]
        values = values[1:]
        retval = dict(zip(value[::2],value[1::2]))
        retval['type'] = type
        return retval

    def _clean_string(self, value, remove_unit=False):
        command_end_pos = value.find(" ")
        if value.find("INSP") != -1:
            value = value.split('"')[1]
            value_begin_pos = value.find(":")
            value = value[value_begin_pos+1:]
            value = value.strip()
        else:
            value = value[command_end_pos+1:]
            if remove_unit:
                unit_begin_pos = value.rfind(" ")
                value = value[:unit_begin_pos]
        return value


    def decimal_to_visa_string(self, value):
        value = float(value)
        return "{:.2E}".format(value)
