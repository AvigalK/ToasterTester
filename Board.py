
import Test_Extractor as te


class Board:

    def __init__(self, serial_number, file_rtt_log, target_dict):
        self.serial_number = serial_number
        self.is_damaged = False
        self.extractor = te.Extractor(file_rtt_log, target_dict)
        self.vdig = [None, None]
        self.burn = [None]
        # rtt attributes
        self.current = [None, None, None]
        self.battery_voltage = [None, None, None]
        # TODO - add relevant attributes from rtt
        # ERROR messages?
        self.errors = []
        # todo - what else in the class?
        self.bluetooth = [None]
        self.imu = [None]
        self.snc = [None]


