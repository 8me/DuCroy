#!/usr/bin/env python

import visa


class Osci(object):

    def __init__(self, ip):
        rm = visa.ResourceManager('@py')
        self.visa_interface = rm.open_resource("TCPIP0::{}::INSTR".format(ip))

    def write(self, command, channel=None, value=None, unit=None):
        if channel is not None:
            command = channel + ":" + command
        if value is not None:
            command = command + " " + value
        if unit is not None:
            command = command + unit
        try:
            self.visa_interface.write(command)
        except:
            print("Invalid combination of commands!")

    def read(self, command, channel=None):
        if channel is not None:
            command = channel + ":" + command
        command = command + "?"
        try:
            return self.visa_interface.query(command)
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
        readback = self.visa_interface.query(command)
        readback = readback.replace("")


    def decimal_to_visa_string(self, value):
        value = float(value)
        return "{:.2E}".format(value)
