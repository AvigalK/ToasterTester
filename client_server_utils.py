

# TODO - add signin method?


import requests as rq
import json

class Test:  # RTT logs analyzer
    def __init__(self, name, cond_to_pass, value=None):
        self.name = name  # string
        self.value = value  # float/None
        self.is_pass = True if cond_to_pass else False  # True/False

    def get_info(self):
        return [self.name, self.value, self.is_pass]

# TODO add support for rtt data from flashboard
class Extractor:  # extracting data from RTT logs
    def __init__(self, infile, target_dict):
        self.infile = infile  # list of lines from txt file
        self.targets = target_dict
        #elf.res = self.get_relevant_lines()
        #self.test_res = self.test()

    def get_relevant_lines(self):
        res = [[] for _ in range(len(self.targets))]
        for line in self.infile:
            for p, target in enumerate(self.targets):
                if target in line:
                    try:
                        end = line.find('\n')
                    except:
                        end = len(line) - 1
                    res[p].append(float(line[line.find(target) + len(target) + 1:end]))
        return res

    # TODO - add calculation for strings such as TWI
    @staticmethod
    def calculate_attribute(self, attr_vals):
        if type(attr_vals[0]) == float:
            attr_value = sum(attr_vals) / len(attr_vals)
        else:
            attr_value = attr_vals[0]
        return attr_value

    def test(self):
        board_attributes_list = []
        attribute_values = []
        attribute_lines = self.get_relevant_lines()
        for attr in attribute_lines:
            attribute_values.append(self.calculate_attribute(self, attr))

        for idx, attribute in enumerate(attribute_values):
        # initializing all required tests
            # TODO get from guy specificaitions for required tests from RTT logs
            # TODO - add string tests such as TWI
            if idx == 0: # current
                t_current = Test(self.targets[idx], attribute > 15, attribute)
                board_attributes_list.append(t_current.get_info)
            if idx == 1: # charger state
                t_charge_state = Test(self.targets[idx], attribute != 12, attribute)
                board_attributes_list.append(t_charge_state.get_info)
            if idx == 2: # battery voltage
                t_battery_volt = Test(self.targets[idx], attribute > 3950, attribute)
                board_attributes_list.append(t_battery_volt.get_info)

        return board_attributes_list


class Board:

    #def __init__(self, serial_number, vdig, burn, file_rtt_log, target_dict):
    def __init__(self, serial_number, file_rtt_log, target_dict):
        self.serial_number = serial_number
        self.is_damaged = False
        self.extractor = Extractor(file_rtt_log, target_dict)
        #self.values = self.extracted.res
        #self.rtt_test_res = self.extracted.test_res
        self.vdig = [0, False]
        self.burn = [False]
        # TODO - remove these unnecessary attributes?
        self.current = None
        self.charger_state = None
        self.battery_voltage = None
        # TODO - add relevant attributes from rtt
        #self.bluetooth = bluetooth
        #self.imu = imu
        #self.snc = snc
        # todo - what else in the class?

    def get_board(self):
        return self

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)




# Creates an array of 9 JSONs for a panel
def convert_panel_to_json(board_list):
    panel_list_json = []
    for board in board_list:
        panel_list_json.append(board.to_json())
    return panel_list_json


# TODO - copmplete function
def send_panel(panel):
    api_url = ""  # TODO - add server's url
    headers = {"Content-Type": "application/json"}
    response = rq.post(api_url, data=panel, headers=headers)
    # todo - get response? check if correct?


