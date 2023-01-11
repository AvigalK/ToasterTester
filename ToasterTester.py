import sys
import streamlit as st
import pandas as pd
from Board import *
from test_parameters import *
from FlashBoard import *


# TODO - write true serial number generator - and move to Server code class
def generateSerialNumber(serial_number, offset):
    # return 0x08
    # return hex(int(serial_number) + offset)
    serial_lst = serial_number.split(' ')
    # if len(serial_number)==2:
    #     sn = int(serial_number[:-1])

    if len(serial_lst) > 1:
        sn = int(serial_lst[offset])
    else:
        sn = int(serial_number) + offset

    return sn

def extractSerialNumber(index, pcb):
    pcb.selectBoard(index)
    fc = FlashActions()
    sn = fc.getSerial()
    #sn = 587
    #sn = api.read_u32(0x10001080)
    # if len(serial_lst) > 1:
    #     sn = int(serial_lst[offset])
    # else:
    #     sn = int(serial_number) + offset
    #print(f"SERIAL read {sn}")
    return sn


class Tee(object):
    def __init__(self, *files):
        self.files = files

    def write(self, obj):
        for f in self.files:
            if type(f) == bytes:
                f.buffer.write(obj)
                f.buffer.flush()
            else:
                f.write(obj)
                f.flush()

    def flush(self):
        for f in self.files:
            f.flush()

    def close(self):
        for f in self.files:
            f.close()


class ToasterTester:

    def __init__(self, num_of_boards, is_gui, is_fake):
        self.num_of_boards = num_of_boards
        self.num_of_damaged_boards = 0
        self.with_gui = is_gui
        self.is_fake_test = is_fake
        self.boards_list = []
        self.boards_result_table = None

    def is_board_damaged(self, board):
        fails = []
        print("===========================================================================\n")
        print("Results:")
        label = []
        result = []
        print(vars(board).keys())
        print(vars(board).items())
        for (name, item) in zip(vars(board).keys(), vars(board).items()):

            if name in ['serial_number', 'errors']:
                label.append(name)
                result.append(item[-1])
            elif name in ['extractor', 'is_damaged']:
                pass
            else:
                if len(item[-1]) > 2:

                    item = item[-1][1:]
                    label.append(name)
                    result.append([item[0],"PASS" if item[-1] is True else "FAIL"])

                elif len(item[-1])==2:
                    label.append(name)
                    result.append([item[-1][0],"PASS" if item[-1][-1] is True else "FAIL"])
                else: #len=1
                    label.append(name)
                    #print(f'item: {item}')
                    result.append("PASS" if item[-1][0] is True else "FAIL")

        res = "\n".join("{} {}".format(x, y) for x, y in zip(label, result))
        res_dict = dict(zip(label, result))
        print(res)
        print("\n===========================================================================\n")
        for idx, attr_values in vars(board).items():
            #print(attr_values)
            if type(attr_values) == list and attr_values != []:
                fails.append(attr_values[-1])
            else:
                fails.append(attr_values)
        print(f"fails: {fails}")
        if False in fails[3:]:
            board.is_damaged = True

        return board.is_damaged, res_dict

    # def create_fake_boards(self, serial_number):
    #     # TODO - check the type of charger_state
    #     board_0 = Board(generateSerialNumber(serial_number, 0), None, None)
    #     board_0.vdig, board_0.burn = [0.0, False], [False]
    #     board_0.current, board_0.charger_state, board_0.battery_voltage = ['current', 7, False], ['charger state', 1,
    #                                                                                               True], [
    #                                                                           'battery voltage', 3407, True]
    #     board_1 = Board(generateSerialNumber(serial_number, 1), None, None)
    #     board_1.vdig, board_1.burn = [1.8, True], [True]
    #     board_1.current, board_1.charger_state, board_1.battery_voltage = ['current', 15, True], ['charger state', 1,
    #                                                                                               True], [
    #                                                                           'battery voltage', 3502, True]
    #     board_2 = Board(generateSerialNumber(serial_number, 2), None, None)
    #     board_2.vdig, board_2.burn = [3.5, True], [True]
    #     board_2.current, board_2.charger_state, board_2.battery_voltage = ['current', 15, True], ['charger state', 1,
    #                                                                                               True], [
    #                                                                           'battery voltage', 1450, False]
    #     # board_0 = cs_utils.Board(100000, data_utils.VDIG("ERR_VDIG", 0), data_utils.Burn("ERR_BURN"), infile, target_dict)
    #     # board_1 = cs_utils.Board(100001, data_utils.VDIG("SUCC_VDIG", 1.8), data_utils.Burn("SUCC_BURN"), infile, target_dict)
    #     # board_2 = cs_utils.Board(100002, data_utils.VDIG("SUCC_VDIG", 3.5), data_utils.Burn("ERR_BURN"), infile, target_dict)
    #     return [board_0, board_1, board_2]

    def run_tests(self, tester_screen):

        # self.boards_result_table = pd.DataFrame(
        #     ["" for i in range(self.num_of_boards)], columns=["Is Board Damaged", "Current"])
        columns = ["Vdig", "Flashing", "Current", "Battery Voltage", "Bluetooth", "IMU signals", "SNC signals", "Is Board Damaged"]

        self.boards_result_table = pd.DataFrame([["" for i in range(len(columns))] for i in range(1,self.num_of_boards+1)],
                                                columns=columns)
        # self.boards_result_table = pd.DataFrame(columns=["Is Board Damaged", "Current"])
        if self.is_fake_test:
            self.run_fake_tests(tester_screen)
        if not self.is_fake_test:
            self.run_real_tests(tester_screen)

    # def run_fake_tests(self, tester_screen):
    #
    #     self.boards_list = self.create_fake_boards(st.session_state.serial_number)
    #     if self.with_gui:
    #         self.run_fake_tests_with_gui(tester_screen)
    #     if not self.with_gui:
    #         self.run_fake_tests_without_gui()

    # def run_fake_tests_with_gui(self, tester_screen):
    #
    #     for i in range(len(self.boards_list)):
    #         tester_screen.show_board_in_work_message(i)
    #         # tester_screen.show_progress_bar(100)
    #         if self.is_board_damaged(self.boards_list[i]):
    #             tester_screen.show_board_damaged_message(i)
    #             self.num_of_damaged_boards = self.num_of_damaged_boards + 1
    #             self.boards_result_table.iloc[[i]] = "DAMAGED"
    #         else:
    #             tester_screen.show_board_ok_message(i)
    #             self.boards_result_table.iloc[[i]] = "OK"
    #         time.sleep(1)
    #     time.sleep(1)

    # def run_fake_tests_without_gui(self):
    #
    #     for i in range(len(fake_boards)):
    #         if self.is_board_damaged(self.boards_list[i]):
    #             self.num_of_damaged_boards = self.num_of_damaged_boards + 1
    #             self.boards_result_table.iloc[[i]] = "DAMAGED"
    #         else:
    #             self.boards_result_table.iloc[[i]] = "OK"
    #     # time.sleep(1)
    #     print(self.boards_result_table)  # todo - delete

    def run_real_tests(self, tester_screen):

        # TODO - get the actual strings out of here to a different code file
        infile_name = 'rtt_log_tested'
        target_dict = {'current': r'current : ',
                       'battery voltage': r'battery voltage: ', 'battery percentage': r'Battery SOC = ',
                       'errors': r'<error>'}

        # TODO - write real test turn
        if self.with_gui:
            self.run_real_tests_with_gui(infile_name, target_dict, tester_screen)
        # if not self.with_gui:
        #     self.run_real_tests_without_gui(infile_name, target_dict)

    def run_real_tests_with_gui(self, infile_name, target_dict, tester_screen):
        print("*************************************************************")
        print(f'MODE of testing: {st.session_state.mode}')
        print("*************************************************************")

        ser = serial.Serial(arduino_port.device, baudrate=57600)

        pcb = pcbControl(ser)
        # import datetime
        from datetime import datetime
        # from datetime import date
        jump = 1 if st.session_state.slot_setup == "all slots" else 2
        rng = self.num_of_boards if st.session_state.slot_setup == "all slots" else (self.num_of_boards * 2) - 1
        for i in range(0, rng, jump):
            # print(st.session_state.serial_number)
            if st.session_state.mode == 'with flash':
                serial_number = generateSerialNumber(st.session_state.serial_number, int(i/jump))
            else: # read serial number from board in position i
                serial_number = extractSerialNumber(i, pcb)
                st.session_state.serial_number = serial_number

            infile_path = f"{test_parameters.main_dir}{infile_name}_{serial_number}.txt"
            infile = open(infile_path, 'w+')
            time_format = datetime.now()
            #time_format = time_format.strftime("%d%m%Y_%H:%M")
            time_format = time_format.strftime("%Y%m%d_%H:%M")
            if serial_number!=0:

                outfile_path = f"{test_parameters.main_dir}rtt_log_{serial_number}_{time_format}.txt"
                #outfile_path = f"{test_parameters.main_dir}rtt_log_{serial_number}.txt"
                outfile = open(outfile_path, 'w+')

            else:
                outfile_path = f"{test_parameters.main_dir}noboard.txt"
                outfile = open(outfile_path, 'w+')


            sys.stdout = Tee(sys.stdout, outfile)

            sys.stdout.write("-----------------------------------------------------\n")
            sys.stdout.write(str(time_format))
            sys.stdout.write("\n-----------------------------------------------------\n")

            tester_screen.show_board_in_work_message(i)
            board = Board(serial_number, infile, target_dict)
            test_res = testBoard(board, i, serial_number, pcb, st.session_state.mode, tester_screen)

            self.boards_list.append(test_res)
            #print(self.boards_list)
            # if jump == 2 and i>0:
            #     print(f'i={i}')
            #     is_damaged, results = self.is_board_damaged(self.boards_list[int(i/jump)])
            # else:
            is_damaged, results = self.is_board_damaged(self.boards_list[int(i/jump)])
            if is_damaged:
                tester_screen.show_board_damaged_message(i)
                self.num_of_damaged_boards = self.num_of_damaged_boards + 1

                self.boards_result_table.iloc[[int(i/jump)],[-1]] = "DAMAGED"
            else:
                tester_screen.show_board_ok_message(i)
                self.boards_result_table.iloc[[int(i/jump)],[-1]] = "OK"

            self.boards_result_table.iloc[[int(i/jump)], [0]] = results['vdig'][1]
            self.boards_result_table.iloc[[int(i/jump)], [1]] = results['burn']
            self.boards_result_table.iloc[[int(i/jump)], [2]] = results['current'][1]
            self.boards_result_table.iloc[[int(i/jump)], [3]] = results['battery_voltage'][1]
            self.boards_result_table.iloc[[int(i/jump)], [4]] = results['bluetooth']
            self.boards_result_table.iloc[[int(i/jump)], [5]] = results['imu']
            self.boards_result_table.iloc[[int(i/jump)], [6]] = results['snc']



            time.sleep(1)
            sys.stdout = sys.__stdout__
            outfile.close()



    # def run_real_tests_without_gui(self, infile, target_dict):
    #     for i in range(self.num_of_boards):
    #         serial_number = generateSerialNumber(LAST_SN, i)
    #         board = Board(serial_number, infile, target_dict)
    #         self.boards_list.append(testBoard(board, i, infile, target_dict))
    #
    #         if self.is_board_damaged(self.boards_list[i]):
    #             self.num_of_damaged_boards = self.num_of_damaged_boards + 1
    #             self.boards_result_table.iloc[[i]] = "DAMAGED"
    #         else:
    #             self.boards_result_table.iloc[[i]] = "OK"

