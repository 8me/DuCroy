#!/usr/bin/env python

import visa
import numpy as np
import h5py

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

    @staticmethod
    def save_waveforms_to_file(filepath, data_array, hor_interval, vert_gain, comment=None):
        with h5py.File(filepath, "w") as file:
            file.attrs[u'vertical_gain'] = vert_gain
            file.attrs[u'horizontal_interval'] = hor_interval
            if comment is not None:
                file.attrs[u'comment'] = comment
            file.create_dataset('waveforms', data=data_array)
    @staticmethod
    def read_waveforms_from_file(filepath):
        retval = dict()
        with h5py.File(filepath, "r") as file:
            retval['vertical_gain'] = float(file.attrs[u'vertical_gain'])
            retval['horizontal_interval'] = float(file.attrs[u'horizontal_interval'])
            retval['comment'] = str(file.attrs[u'comment'])
            retval['data'] = np.asarray(file['waveforms'])
        return retval

    def set_sequence_mode(self, sequences):
        command = "SEQ"
        argument = ""
        if sequences is None:
            argument = "OFF"
        else:
            argument = "ON," + str(sequences)
        self.write(command,value=argument)

        return self.get_number_of_sequences()

    def get_number_of_sequences(self):
        sequence_info = self._read_sequence_info()
        if sequence_info[0] == 'OFF':
            return None
        else:
            return int(sequence_info[1])

    def get_number_of_sweeps(self):
        command = "PAST? CUST, SWEEPS"
        self.write(command)
        readback = self.visa_if.read_raw().decode('ascii')
        readback = readback.replace("PAST CUST,SWEEPS,", "")
        readback = readback.strip().split(',')
        retval = []
        for value in readback:
            if value == 'UNDEF':
                retval.append(None)
            else:
                retval.append(float(value))
        return retval

    def clear_sweeps(self):
        self.write("CLSW;")

    def get_measure(self, measure_channel):
        command = "PAST? CUST," + measure_channel
        self.write(command)
        readback = self.visa_if.read_raw().decode('ascii')
        readback = readback.replace("PAST CUST,"+measure_channel+",","")
        readback = readback.split(",")
        retval = dict(zip(readback[2::2],readback[3::2]))
        for key, value in retval.items():
            if key != 'SWEEPS':
                if value.find("UN") >= 0:
                    retval[key] = None
                else:
                    unit_begin_pos = value.rfind(" ")
                    value = value[:unit_begin_pos]
                    retval[key] = float(value)
            else:
                value = value.strip()
                retval[key] = int(value)

        self.write("CLSW;")
        return retval


    def aquire_waveforms(self, channels, number_of_waveforms):
        """Aquire a certain amount of waveforms, without being limited to the sequence memory of the oscilloscope
        Parameters
        ----------
        channels (string): list of channels where the data to read from
        number_of_waveforms (int): the amount of waveforms to record
        Returns
        -------
        sequences: two dimensional array with the waveforms as ADC values
        """
        number_of_sequences = self.set_sequence_mode(500)
        sequences = [np.array([])]*len(channels)
        for i in range(number_of_waveforms//number_of_sequences):
            self.record_waveforms()
            for id, channel in enumerate(channels):
                run_sequences = self.get_waveform_memory(channel)
                sequences[id] = np.reshape( np.append(sequences[id],run_sequences) , (-1,run_sequences.shape[1]))
        return sequences




    def record_waveforms(self):
        command = "ARM; WAIT;"
        self.write(command)

    def get_waveform_memory(self, channel):
        command = channel + ":WF? DAT1"
        sequences = self.get_number_of_sequences()
        readback = self.visa_if.query_binary_values(command, datatype='b')
        samples = int(len(readback)/sequences)
        return np.reshape(readback, (sequences,samples))


    def get_samples_per_wf(self):
        sequence_info = self._read_sequence_info()
        print(sequence_info)
        return int(float(sequence_info[-1]))+2

    def _read_sequence_info(self):
        command = "SEQ"
        readback = self.read(command)
        readback = self._clean_string(readback, True)
        return readback.split(',')

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
        trigger_source = trigger_settings['SR']
        trigger_settings.clear()
        trigger_settings['TYPE'] = 'EDGE'
        trigger_settings['SR'] = trigger_source
        if events is None:
            trigger_settings['HT'] = "OFF"
        else:
            trigger_settings['HT'] = 'EV'
            trigger_settings['HV'] = str(events)
        self._write_trigger_select(trigger_settings)

    def set_trigger_slope(self, slope, channel=None):
        """Sets the trigger slope
        Returns
        -------
        slope: slope afterwards as string
        """
        command = "TRSL"
        if channel is None:
            current_settings = self._read_trigger_select()
            channel = current_settings['SR']
        self.write(command, channel, slope)
        retval = self.get_trigger_slope()
        return retval

    def get_trigger_slope(self, channel=None):
        """Gets the trigger slope
        Returns
        -------
        slope: current slope setting as string
        """
        command = "TRSL"
        if channel is None:
            current_settings = self._read_trigger_select()
            channel = current_settings['SR']
        readback = self.read(command, channel)
        readback = self._clean_string(readback)
        return readback

    def set_trigger_source(self, channel):
        """Sets the trigger source
        Returns
        -------
        source: the new trigger source
        """
        current_settings = self._read_trigger_select()
        current_settings['SR'] = channel
        self._write_trigger_select(current_settings)
        current_settings = self._read_trigger_select()
        return current_settings['SR']

    def get_trigger_source(self):
        """Returns the trigger source
        Returns
        -------
        source: current trigger source
        """
        current_settings = self._read_trigger_select()
        return current_settings['SR']

    def set_trigger_level(self, level, channel):
        """Sets the trigger level
        Returns
        -------
        level: new trigger_level float [V]
        """
        command = "TRLV"
        level_string = self.decimal_to_visa_string(level)
        if channel is None:
            current_settings = self._read_trigger_select()
            channel = current_settings['SR']
        self.write(command, channel, level_string)
        readback = self.get_trigger_level()
        return readback

    def get_trigger_level(self, channel=None):
        """Reads the trigger level
        Returns
        -------
        level: float [V]
        """
        command = "TRLV"
        if channel is None:
            current_settings = self._read_trigger_select()
            channel = current_settings['SR']
        readback = self.read(command,channel)
        readback = self._clean_string(readback,True)
        return readback

    def _write_trigger_select(self, settings):
        command = "TRSE"
        argument = ""
        for key, value in settings.items():
            if argument != "":
                argument += ','
            if key != 'TYPE':
                argument += key + ',' + value
        argument = settings['TYPE'] + ',' + argument
        self.write(command, value=argument)


    def _read_trigger_select(self):
        command = "TRSE"
        readback = self.read(command)
        readback = self._clean_string(readback)
        readback = readback.strip()
        values = readback.split(",")
        type = values[0]
        values = values[1:]
        retval = dict(zip(values[::2],values[1::2]))
        retval['TYPE'] = type
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
        return value.strip()


    def decimal_to_visa_string(self, value):
        value = float(value)
        return "{:.2E}".format(value)
