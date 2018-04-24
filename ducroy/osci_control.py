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

    def set_channel_gain(self, voltage, channel):
        command = "VDIV"
        voltage_string = self.decimal_to_visa_string(voltage)
        self.write(command, channel, voltage_string, "V")
        readback = self.read(command,channel)
        readback = readback.replace(channel+":"+command,"")
        readback = readback.replace("V","")
        return float(readback)


    def decimal_to_visa_string(self, value):
        value = float(value)
        return "{:.2E}".format(value)
