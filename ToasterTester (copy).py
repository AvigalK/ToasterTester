import streamlit as st
import pandas as pd
import time

# import Tester_Extractor as te
from Board import *
from test_parameters import *
from FlashBoard import *


# TODO - write true serial number generator - and move to Server code class
def getNextSerialNumber(serial_number, offset):
    # return 0x08
    # print(type(0x01))
    # print(((int(serial_number))))
    return (int(serial_number) + offset)


class ToasterTester:

    def __init__(self, num_of_boards, is_gui, is_fake):
        self.num_of_boards = num_of_boards
        self.num_of_damaged_boards = 0
        self.with_gui = is_gui
        self.is_fake_test = is_fake
        self.boards_list = []
        self.boards_result_table = None

    # TODO - adapt to damaged as we want it
    def is_board_damaged(self, board):
        fails = []
        print(f'FROM IS DAMAGED, atrr_values = {vars(board).items()}')
        for idx, attr_values in vars(board).items():
            print(attr_values)
            if type(attr_values) == list and attr_values != []:
                fails.append(attr_values[-1])
            else:
                fails.append(attr_values)
        print(f"fails: {fails}")
        if False in fails[3:]:
            board.is_damaged = True
            # if type(attr_values) == list:  # attributes
            #     if len(attr_values) == 2:  # vdig
            #         if not attr_values[1]:
            #             board.is_damaged = True
            #     elif len(attr_values) == 1:  # burn
            #         if not attr_values[0]:
            #             board.is_damaged = True
            #     else:
            #         if not attr_values[-1]:  # every other attribute from rtt logs
            #             board.is_damaged = True

        # attributes_names_list = [attr for attr in dir(board) if not attr.startswith('__')]
        return board.is_damaged
        # return True if board.is_damaged is True else False

    def create_fake_boards(self, serial_number):
        # TODO - check the type of charger_state
        board_0 = Board(getNextSerialNumber(serial_number, 0), None, None)
        board_0.vdig, board_0.burn = [0.0, False], [False]
        board_0.current, board_0.charger_state, board_0.battery_voltage = ['current', 7, False], ['charger state', 1,
                                                                                                  True], [
                                                                              'battery voltage', 3407, True]
        board_1 = Board(getNextSerialNumber(serial_number, 1), None, None)
        board_1.vdig, board_1.burn = [1.8, True], [True]
        board_1.current, board_1.charger_state, board_1.battery_voltage = ['current', 15, True], ['charger state', 1,
                                                                                                  True], [
                                                                              'battery voltage', 3502, True]
        board_2 = Board(getNextSerialNumber(serial_number, 2), None, None)
        board_2.vdig, board_2.burn = [3.5, True], [True]
        board_2.current, board_2.charger_state, board_2.battery_voltage = ['current', 15, True], ['charger state', 1,
                                                                                                  True], [
                                                                              'battery voltage', 1450, False]
        # board_0 = cs_utils.Board(100000, data_utils.VDIG("ERR_VDIG", 0), data_utils.Burn("ERR_BURN"), infile, target_dict)
        # board_1 = cs_utils.Board(100001, data_utils.VDIG("SUCC_VDIG", 1.8), data_utils.Burn("SUCC_BURN"), infile, target_dict)
        # board_2 = cs_utils.Board(100002, data_utils.VDIG("SUCC_VDIG", 3.5), data_utils.Burn("ERR_BURN"), infile, target_dict)
        return [board_0, board_1, board_2]

    def run_tests(self, tester_screen):

        self.boards_result_table = pd.DataFrame(
            ["" for i in range(self.num_of_boards)],
            columns=["Is Board Damaged"])
        if self.is_fake_test:
            self.run_fake_tests(tester_screen)
        if not self.is_fake_test:
            self.run_real_tests(tester_screen)

    def run_fake_tests(self, tester_screen):

        self.boards_list = self.create_fake_boards(st.session_state.serial_number)
        if self.with_gui:
            self.run_fake_tests_with_gui(tester_screen)
        if not self.with_gui:
            self.run_fake_tests_without_gui()

    def run_fake_tests_with_gui(self, tester_screen):

        for i in range(len(self.boards_list)):
            tester_screen.show_board_in_work_message(i)
            tester_screen.show_progress_bar(100)
            if self.is_board_damaged(self.boards_list[i]):
                tester_screen.show_board_damaged_message(i)
                self.num_of_damaged_boards = self.num_of_damaged_boards + 1
                self.boards_result_table.iloc[[i]] = "DAMAGED"
            else:
                tester_screen.show_board_ok_message(i)
                self.boards_result_table.iloc[[i]] = "OK"
            time.sleep(1)
        time.sleep(1)

    def run_fake_tests_without_gui(self):

        for i in range(len(fake_boards)):
            if self.is_board_damaged(self.boards_list[i]):
                self.num_of_damaged_boards = self.num_of_damaged_boards + 1
                self.boards_result_table.iloc[[i]] = "DAMAGED"
            else:
                self.boards_result_table.iloc[[i]] = "OK"
        # time.sleep(1)
        print(self.boards_result_table)  # todo - delete

    def run_real_tests(self, tester_screen):

        # TODO - get the actual strings out of here to a different code file
        infile = open(f'rtt_log_tested.txt', 'w+')
        target_dict = {'current': r'current : ',
                       'battery voltage': r'battery voltage: ', 'battery percentage': r'Battery SOC = '
                       , 'errors': r'error'}

        # TODO - write real test turn
        if self.with_gui:
            self.run_real_tests_with_gui(infile, target_dict, tester_screen)
        if not self.with_gui:
            self.run_real_tests_without_gui(infile, target_dict)

    # TODO - change serial number logic
    def run_real_tests_with_gui(self, infile, target_dict, tester_screen):
        for i in range(self.num_of_boards):

            serial_number = getNextSerialNumber(st.session_state.serial_number, i)
            infile = open(f'/home/wld-hw/rpi_band_tester/rtt_log_tested_{serial_number}.txt', 'w+')
            #sys.stdout = open(f'/home/wld-hw/rpi_band_tester/rtt_log_{serial_number}.txt', 'w+')
            sys.stdout.write("-----------------------------------------------------\n")
            import datetime
            sys.stdout.write(str(datetime.datetime.now()))
            sys.stdout.write("\n-----------------------------------------------------\n")
            tester_screen.show_board_in_work_message(i)
            board = Board(serial_number, infile, target_dict)
            # TODO - add some progress bar mechanism
            test_res = testBoard(board, i, infile, target_dict)
            self.boards_list.append(test_res)

            if self.is_board_damaged(self.boards_list[i]):
                tester_screen.show_board_damaged_message(i)
                self.num_of_damaged_boards = self.num_of_damaged_boards + 1
                self.boards_result_table.iloc[[i]] = "DAMAGED"
            else:
                tester_screen.show_board_ok_message(i)
                self.boards_result_table.iloc[[i]] = "OK"
            time.sleep(1)
            #sys.stdout.close()
        # time.sleep(1)

    # TODO - change serial number logic
    def run_real_tests_without_gui(self, infile, target_dict):
        for i in range(self.num_of_boards):
            serial_number = getNextSerialNumber(LAST_SN, i)
            board = Board(serial_number, infile, target_dict)
            self.boards_list.append(testBoard(board, i, infile, target_dict))

            if self.is_board_damaged(self.boards_list[i]):
                self.num_of_damaged_boards = self.num_of_damaged_boards + 1
                self.boards_result_table.iloc[[i]] = "DAMAGED"
            else:
                self.boards_result_table.iloc[[i]] = "OK"
        # time.sleep(1)