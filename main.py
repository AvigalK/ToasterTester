
import tester
import pandas as pd
import numpy as np

import streamlit as st
import time

import client_server_utils as cs_utils
import data_utils
# from FlashBoard import *


WITH_GUI = False
FAKE_BOARDS = True
NUM_OF_BOARDS = 3  # TODO - change in the end to 9


# TODO - write true serial number generator
def getNextSerialNumber():
    return 0x09


# TODO - adapt to damaged as we want it
def is_board_damaged(board):
    return True if board.is_damaged is True else False
    #members_list = [member1, member2]


if __name__ == '__main__':

    if WITH_GUI:
        st.title("Toaster-Tester")
        st.text("This is an automatic tester for a individual panel of board.")
        st.text("Please Run the following tests and wait.")
        st.text("")
        st.caption("When finished - please send the result to the server, ")
        st.caption("and if you get a successful response - please replace the panel and move on to the next one.")
        st.text("")
        st.text("")
        clicked_run_test = st.button("Run Tests on Panel")
    else:
        clicked_run_test = True

    infile = open('parse.txt', 'r')
    target_dict = {'current': r'current :', 'charger state': r'charger state :', 'battery voltage': r'battery voltage:'}

    # TODO - DELETE, this is a fake test run
    if FAKE_BOARDS is True:
        board_0 = cs_utils.Board(100000, infile, target_dict)
        board_0.vdig, board_0.burn = [0.0, False], False
        board_1 = cs_utils.Board(100001, infile, target_dict)
        board_1.vdig, board_1.burn = [1.8, True], True
        board_2 = cs_utils.Board(1000002, infile, target_dict)
        board_2.vdig, board_2.burn = [3.5, True], False
        #board_0 = cs_utils.Board(100000, data_utils.VDIG("ERR_VDIG", 0), data_utils.Burn("ERR_BURN"), infile, target_dict)
        #board_1 = cs_utils.Board(100001, data_utils.VDIG("SUCC_VDIG", 1.8), data_utils.Burn("SUCC_BURN"), infile, target_dict)
        #board_2 = cs_utils.Board(100002, data_utils.VDIG("SUCC_VDIG", 3.5), data_utils.Burn("ERR_BURN"), infile, target_dict)
        list_of_boards = [board_0, board_1, board_2]

        num_of_damaged_boards = 0
        boards_table = pd.DataFrame(
            ["" for i in range(len(list_of_boards))],
            columns=["Is Board Damaged"])
        # print(boards_table) # todo - delete
        for i in range(len(list_of_boards)):
            if WITH_GUI:
                time.sleep(1)
                st.write(f"Working on board number {i}...")
                progress_bar = st.progress(0)
                for percent_complete in range(100):
                    time.sleep(0.05)
                    progress_bar.progress(percent_complete + 1)
            if is_board_damaged(list_of_boards[i]):
                if WITH_GUI:
                    st.error(f"Board number {i+1} is DAMAGED.")
                num_of_damaged_boards = num_of_damaged_boards+1
                boards_table.iloc[[i]] = "DAMAGED"
            else:
                if WITH_GUI:
                    st.success(f"Board number {i+1} is OK.")
                boards_table.iloc[[i]] = "OK"
                time.sleep(1)
        #time.sleep(2)
            # print(boards_table)  # todo - delete

    else:
        if clicked_run_test is True:

            # TODO - write real test turn
            num_of_damaged_boards = 0
            list_of_boards = []
            boards_table = pd.DataFrame(
                ["" for i in range(len(list_of_boards))],
                columns=["Is Board Damaged"])
            for i in range(NUM_OF_BOARDS):
                time.sleep(1)
                serial_number = getNextSerialNumber()
                board = cs_utils.Board(serial_number, infile, target_dict)
                if WITH_GUI:
                    st.write(f"Working on board number {i}...")
                list_of_boards.append(testBoard(board, i))
                '''
                progress_bar = st.progress(0)
                for percent_complete in range(100):
                    time.sleep(0.05)
                    progress_bar.progress(percent_complete + 1)
                '''
                if WITH_GUI:
                    if is_board_damaged(list_of_boards[i]):
                        st.error(f"Board number {i+1} is DAMAGED.")
                        num_of_damaged_boards = num_of_damaged_boards+1
                        boards_table.iloc[[i]] = "DAMAGED"
                    else:
                        st.success(f"Board number {i+1} is OK.")
                        boards_table.iloc[[i]] = "OK"
                    time.sleep(1)

        if WITH_GUI:
            st.header("Results:")
            st.text("")
            st.table(boards_table)
            time.sleep(1)

            if num_of_damaged_boards > 0:
                st.error(f"The panel is DAMAGED, with {num_of_damaged_boards} damaged boards out of {len(list_of_boards)}.")
            else:
                st.success(f"The panel is OK, with no damaged boards.")

            clicked_send_result = st.button("Send Result to Server")
            if clicked_send_result:
                # TODO - DELETE, this is a fake response
                response = 200
                st.write(f"Got {response}.")
                # TODO - insert the code for sending the JSONs array to server
                # client_server_test.send_panel()
                # TODO - wait for response and show it on screen
                # TODO - understand what to do for multiple buttons, as it refreshes

        else:
            print(boards_table)


