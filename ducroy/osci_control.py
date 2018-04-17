import visa



class Osci(object):

    def __init__(self, ip):
        rm = visa.ResourceManager('@py')
        self.visa_interface = rm.open_resource("TCPIP0::{}::INSTR".format(ip))

    
