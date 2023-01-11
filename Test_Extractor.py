
class Test:  # RTT logs analyzer
    # TODO - check if returns [None. None, None] when error
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
        self.infile.seek(0, 0)
        res = [[] for _ in range(len(self.targets))]
        for line in self.infile:
            #print(f'RTT LINE: {line}')
            for p, target in enumerate(self.targets.values()):
                if target in line:
                    try:
                        end = line.find('\n')
                    except:
                        end = len(line) - 1

                    if p in [0, 1]:
                        res[p].append((line[line.find(target) + len(target)-1:end]))
                    elif p == 2:  # battery soc
                        res[p].append((line[line.find(target) + len(target) - 1:line.find("%")]))
                    elif p == 3:  # errors
                        res[p].append((line[line.find(target):end]))

        return res

    # TODO - add calculation for strings such as TWI
    @staticmethod
    def calculate_attribute(self, attr_vals):
       # print(f'attr values calculated: {attr_vals}')

        if len(attr_vals) > 0:
            attr_value = sum(map(float, attr_vals)) / len(attr_vals)
            return attr_value
        else:
            return "no values"

    def test(self):
        board_attributes_list = []
        attribute_values = []

        attribute_lines = self.get_relevant_lines()
        #print(f'attribute_lines: {attribute_lines}')
        for i, attr in enumerate(attribute_lines):
            if i < len(attribute_lines)-1:
                attribute_values.append(self.calculate_attribute(self, attr))
            else:
                attribute_values.append(attr)

        for idx, attribute in enumerate(attribute_values):
        # initializing all required tests
            # TODO - add ERROR string tests such as TWI
            if attribute == "no values":
                print(f'errors extracted: {attribute}')
            else:
                if idx == 0:  # current
                    print(f'battery soc extracted: {attribute_values[2]}')
                    #print(f'errors extracted: {attribute_values}')

                    t_current = Test(list(self.targets.keys())[idx], float(attribute) > 10 or float(attribute_values[2]) >= 80, float(attribute))
                    #print(t_current.get_info())
                    board_attributes_list.append(t_current.get_info())
                if idx == 1:  # battery voltage
                    t_battery_volt = Test(list(self.targets.keys())[idx], float(attribute) > 3700, float(attribute))
                   # print(t_battery_volt.get_info())
                    board_attributes_list.append(t_battery_volt.get_info())

        return board_attributes_list

