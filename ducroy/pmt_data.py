import h5py
import numpy as np

class PmtData:
    def __init__(self, serial, nominal_voltage=1000, nominal_gain=3e6):
        if serial == "":
            return
        self.filepath = "./{}.h5".format(serial)
        with h5py.File(self.filepath, "w") as file:
            file.attrs[u'serial'] = serial
            file.attrs[u'nominal_voltage'] = nominal_voltage
            file.attrs[u'nominal_gain'] = nominal_gain
            grp_analysis = file.create_group("analysis")
            grp_analysis.attrs[u'measured_nominal_gain'] = -1
            grp_analysis.attrs[u'measured_nominal_gain_err'] = -1
            grp_analysis.attrs[u'measured_nominal_voltage'] =  -1
            grp_analysis.attrs[u'measured_nominal_voltage_err'] = -1

    @property
    def serial(self):
        retval = ''
        with h5py.File(self.filepath, "r") as file:
            retval = str(file.attrs[u'serial'])
        return retval

    @serial.setter
    def serial(self, value):
        with h5py.File(self.filepath, "r+") as file:
            file.attrs[u'serial'] = value

    @property
    def nominal_voltage(self):
        retval = ''
        with h5py.File(self.filepath, "r") as file:
            retval = file.attrs[u'nominal_voltage']
        return retval

    @nominal_voltage.setter
    def nominal_voltage(self, value):
        with h5py.File(self.filepath, "r+") as file:
            file.attrs[u'nominal_voltage'] = value

    @property
    def nominal_gain(self):
        retval = ''
        with h5py.File(self.filepath, "r") as file:
            retval = file.attrs[u'nominal_gain']
        return retval

    @nominal_gain.setter
    def nominal_gain(self, value):
        with h5py.File(self.filepath, "r+") as file:
            file.attrs[u'nominal_gain'] = value


    def _get_analysis_attr(self, key):
        retval = None
        with h5py.File(self.filepath, "r") as file:
            group = file[u'analysis']
            retval = group.attrs[key]
        return retval

    def _set_analysis_attr(self, key, value):
        with h5py.File(self.filepath, "r+") as file:
            group = file[u'analysis']
            group.attrs[key] = value

    @property
    def measured_nominal_voltage(self):
        return self._get_analysis_attr(u'measured_nominal_voltage')

    @measured_nominal_voltage.setter
    def measured_nominal_voltage(self, value):
        self._set_analysis_attr(u'measured_nominal_voltage', value)

    @property
    def measured_nominal_voltage_error(self):
        return self._get_analysis_attr(u'measured_nominal_voltage_err')

    @measured_nominal_voltage_error.setter
    def measured_nominal_voltage_error(self, value):
        self._set_analysis_attr(u'measured_nominal_voltage_err', value)

    @property
    def measured_nominal_gain(self):
        return self._get_analysis_attr(u'measured_nominal_gain')

    @measured_nominal_gain.setter
    def measured_nominal_gain(self, value):
        self._set_analysis_attr(u'measured_nominal_gain', value)

    @property
    def measured_nominal_gain_error(self):
        return self._get_analysis_attr(u'measured_nominal_gain_err')

    @measured_nominal_gain_error.setter
    def measured_nominal_gain_error(self, value):
        self._set_analysis_attr(u'measured_nominal_gain_err', value)

    def add_fit_results(self, hv, used_gaussians, nphe, q0, q0sigma, q1, q1sigma, gain, gain_err):
        dataset_groupname = "/analysis/{:.0f}V".format(hv)
        with h5py.File(self.filepath, "r+") as file:
            dataset_group = None
            if dataset_groupname not in file.keys():
                dataset_group = file.create_group(dataset_groupname)
            else:
                dataset_group = file[dataset_groupname]
            dataset_group.attrs[u'nphe'] = nphe
            dataset_group.attrs[u'used_gaussians'] = used_gaussians
            dataset_group.attrs[u'q0'] = q0
            dataset_group.attrs[u'q0sigma'] = q0sigma
            dataset_group.attrs[u'q1'] = q1
            dataset_group.attrs[u'q1sigma'] = q1sigma
            dataset_group.attrs[u'gain'] = gain
            dataset_group.attrs[u'gain_err'] = gain_err

    def get_fit_results(self, hv):
        retval = dict()
        dataset_groupname = "/analysis/{:.0f}V".format(hv)
        with h5py.File(self.filepath, "r") as file:
            dataset_group = file[dataset_groupname]
            retval[u'nphe'] = file[dataset_groupname].attrs[u'nphe']
            retval[u'used_gaussians'] = file[dataset_groupname].attrs[u'used_gaussians']
            retval[u'q0'] = file[dataset_groupname].attrs[u'q0']
            retval[u'q0sigma'] = file[dataset_groupname].attrs[u'q0sigma']
            retval[u'q1'] = file[dataset_groupname].attrs[u'q1']
            retval[u'q1sigma'] = file[dataset_groupname].attrs[u'q1sigma']
            retval[u'gain'] = file[dataset_groupname].attrs[u'gain']
            retval[u'gain_err'] = file[dataset_groupname].attrs[u'gain_err']
        return retval

    def add_waveforms(self, hv, name, horizontal_interval, vertical_gain, samples, comment=''):
        dataset_groupname = "/raw_data/{0:.0f}V/{1}".format(hv, name)
        with h5py.File(self.filepath, "r+") as file:
            if dataset_groupname not in file.keys():
                dataset_group = file.create_group(dataset_groupname)
            else:
                dataset_group = file[dataset_groupname]
            dataset_group.attrs[u'comment'] = comment
            dataset_group.attrs[u'horizontal_interval'] = horizontal_interval
            dataset_group.attrs[u'vertical_gain'] = vertical_gain
            dataset_group[u'data'] = samples

    def add_histogram(self, hv, x, y):
        dataset_groupname = "/analysis/{:.0f}V".format(hv)
        with h5py.File(self.filepath, "r+") as file:
            dataset_group = None
            if dataset_groupname not in file.keys():
                dataset_group = file.create_group(dataset_groupname)
            else:
                dataset_group = file[dataset_groupname]
            dataset_group[u'histogram'] = (x, y)

    def get_histogram(self, hv):
        retval = None
        dataset_groupname = "/analysis/{:.0f}V/histogram".format(hv)
        with h5py.File(self.filepath, "r") as file:
            retval = np.asarray(file[dataset_groupname])
        return retval

    def get_gains_and_voltages(self):
        hv = []
        gain = []
        with h5py.File(self.filepath, "r") as file:
            analysis = file[u'analysis']
            for key in list(analysis.keys()):
                voltage = int(key.rstrip('V'))
                hv.append(voltage)
                gain.append(self.get_fit_results(voltage)['gain'])
        return (hv,gain)




    @staticmethod
    def read_from_file(filepath):
        retval = PmtData(serial = '')
        retval.filepath = filepath
        return retval
