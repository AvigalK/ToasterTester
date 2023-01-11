# import Test_Extractor as te
import pandas as pd
import streamlit as st
from test_parameters import *
import time


class Screen:

    def __init__(self):
        # initialize SessionState

        if 'test_button_clicked' not in st.session_state:
            st.session_state["test_button_clicked"] = False
        if 'send_results_button_clicked' not in st.session_state:
            st.session_state.send_results_button_clicked = False
        if 'show_next_panel_test_button_clicked' not in st.session_state:
            st.session_state["show_next_panel_test_button_clicked"] = False
        if 'show_restart_panel_button_clicked' not in st.session_state:
            st.session_state.show_restart_panel_button_clicked = False
        if 'serial_number_inserted' not in st.session_state:
            st.session_state.serial_number_inserted = False
        if 'results_table' not in st.session_state:
            st.session_state.results_table = None
        if 'boards_list' not in st.session_state:
            st.session_state.boards_list = None
        if 'serial_number' not in st.session_state:
            st.session_state.serial_number = 0x00
        if 'mode' not in st.session_state:
            st.session_state.mode = 'with flash'
        if 'flashing_toggled' not in st.session_state:
            st.session_state.flashing_toggled = False
        if 'number_of_boards' not in st.session_state:
            st.session_state.number_of_boards = 9
        if 'slot_setup' not in st.session_state:
            st.session_state.slot_setup = "all slots"
        if 'slot_setup_toggled' not in st.session_state:
            st.session_state.slot_setup_toggled = False
        if 'number_of_boards_toggled' not in st.session_state:
            st.session_state.number_of_boards_toggled = False

    def set_slot_setup(self):
        st.session_state.slot_setup_toggled = True

    def set_number_of_boards(self):
        st.session_state.number_of_boards_toggled = True

    def set_flashing_toggled(self):
        st.session_state.flashing_toggled = True

    def set_serial_number_inserted(self):
        st.session_state.serial_number_inserted = True

    def set_run_test_button_was_clicked(self):
        st.session_state.test_button_clicked = True

    def set_send_result_button_was_clicked(self):
        st.session_state.send_results_button_clicked = True

    def set_show_next_panel_test_button_clicked(self):
        st.session_state.show_next_panel_test_button_clicked = True

    def set_show_restart_panel_button_clicked(self):
        st.session_state.show_restart_panel_button_clicked = True

    def show_opening_message(self):
        st.title("Toaster-Tester")
        st.text("This is an automatic tester for a individual panel of board.")
        st.text("Please Run the following tests and wait.")
        st.text("")
        st.caption("When finished - please send the result to the server, ")
        st.caption("and if you get a successful response - please replace the panel and move on to the next one.")
        st.text("")
        st.text("")



    def show_insert_serial_number(self):
        '''
        st.write("st.session_state.serial_number:")
        st.write(st.session_state.serial_number)
        st.write("st.session_state.serial_number_inserted:")
        st.write(st.session_state.serial_number_inserted)
        #if st.session_state.serial_number_inserted:
        #    return True
        '''
        serial_number = st.text_input("Please input the Serial Number: ", value="",
                                      max_chars=MAX_CHARS_SN, key=None, type="default",
                                      on_change=self.set_serial_number_inserted)
        st.session_state.serial_number = serial_number

        return serial_number

    def show_first_serial_number(self):
        st.text("The Serial Number of the first board in this panel is: ")
        st.text(st.session_state.serial_number)
        st.text("")

    def select_slot_setup(self, col):
        with col:
            setup = st.selectbox("Select slot setup for testing", ("all slots", "uneven slots (1,3,5...)"),
                                 on_change=self.set_slot_setup)
        # setup = st.selectbox("Select slot setup for testing", ("all slots", "uneven slots"),
        #                      on_change=self.set_slot_setup)
        st.session_state.slot_setup = setup

        return st.session_state.slot_setup_toggled

    def select_number_of_boards(self, col):
        rang = 10 if st.session_state.slot_setup == 'all slots' else 6
        with col:
            number_of_boards = st.selectbox("Select number of boards for testing", (range(1, rang)),
                                            on_change=self.set_number_of_boards)
        # number_of_boards = st.selectbox("Select number of boards for testing", (range(1, rang)),
        #                                 on_change=self.set_number_of_boards)

        st.session_state.number_of_boards = number_of_boards

        return st.session_state.number_of_boards_toggled

    def toggle_flashing(self, col):

        with col:
            mode = st.selectbox('Select the testing mode', options=['with flash', 'without flash'],
                            key="run_test_button_0", on_change=self.set_flashing_toggled)

        # mode = 'without flash' if clicked else 'with flash'

        st.session_state.mode = mode

        return st.session_state.flashing_toggled

    # def show_num_of_boards_to_test(self):
    #     st.text("The Serial Number of the first board in this panel is: ")
    #     st.text(st.session_state.num_of_bands_to_test)
    #     st.text("")

    # def show_if_serial_number_exists(self, server):
    #     sn_exists = server.check_if_serial_number_exists(st.session_state.serial_number)
    #     if sn_exists:
    #         st.text("This Serial Number already exists on server.")
    #         st.text("Please refreash the page and insert a VALID Serial Number.")
    #         # for i in range(100):
    #         #     st.text("")
    #     else:
    #         st.text("This is a VALID Serial Number. You may continue.")

    def show_run_test_button(self):
        clicked = st.session_state.test_button_clicked or \
                  st.button("Run Tests on Panel", key="run_test_button_2",
                            on_click=self.set_run_test_button_was_clicked)
        # clicked = st.button("Run Tests on Panel", key="run_test_button_2",
        #                     on_click=self.set_run_test_button_was_clicked())
        return clicked

    def show_results_message(self, toaster):
        st.header("Results:")
        st.text("")
        # st.table(toaster.boards_result_table)
        st.table(st.session_state.results_table)
        time.sleep(1)

    def show_result_message(self, toaster, index):
        if not index:
            st.header("Results:")
            st.text("")
        # st.table(toaster.boards_result_table)
        st.table(st.session_state.results_table[index])
        time.sleep(1)

    def show_board_damaged_message(self, num):
        st.error(f"Board number {num + 1} is DAMAGED.")

    def show_board_ok_message(self, num):
        st.success(f"Board number {num + 1} is OK.")

    def show_board_in_work_message(self, num):
        time.sleep(1)
        st.write(f"Working on board number {num + 1}...")

    # def show_progress_bar(self, num):
    #     progress_bar = st.progress(0)
    #     for percent_complete in range(num):
    #         time.sleep(0.05)
    #         progress_bar.progress(percent_complete + 1)
    def show_progress_bar(self, holder, num=0):
        progress_bar = st.progress(num)
        self.show_current_stage(num, holder) if not num else None
        return progress_bar

    def update_progress_bar(self, num, progress_bar, placeholder, stages=7):

        progress_bar.progress(num / stages)
        self.show_current_stage(num, placeholder)

        if num == stages:
            progress_bar.empty()

    def show_current_stage(self, stage_num, placeholder):
        stages = ["Initializing Test", "Flash test", "Checking Vdig", "Checking RTT logs", "Checking Bluetooth",
                  "Checking imu", "Checking snc", "Done"]

        placeholder.empty()
        placeholder.text(stages[stage_num])
        with placeholder.container():
            st.write(stages[stage_num])

    def show_results_damaged(self, num_of_damaged_boards, num_of_boards):
        is_damaged = False
        num_of_damaged_boards = 0
        num_of_boards = st.session_state.results_table.shape[0]
        for i in range(num_of_boards):

            if st.session_state.results_table.iloc[i, -1] == "DAMAGED":
                num_of_damaged_boards = num_of_damaged_boards + 1
                is_damaged = True
        if is_damaged:
            st.error(f"The panel is DAMAGED, with {num_of_damaged_boards} damaged boards out of {num_of_boards}.")
        else:
            st.success(f"The panel is OK, with no damaged boards.")

    def show_send_results_button(self):

        clicked = st.session_state.send_results_button_clicked or \
                  st.button('Send Results to Server', key="send_result_button_1",
                            on_click=self.set_send_result_button_was_clicked)
        # clicked = st.session_state.send_results_button_clicked or \
        #           st.button('Send Results to Server', key="send_result_button_1")
        # clicked = st.button('Send Results to Server', key="send_result_button_1",
        #                     on_click=self.set_send_result_button_was_clicked())

        # clicked = st.form_submit_button('Send Results to Server', on_click=self.set_send_result_button_was_clicked())
        # print(st.session_state.send_results_button_clicked)
        # print(st.session_state["send_results_button_clicked"])
        # print(f'clicked: {clicked}')
        return clicked

    def show_sending_results_in_progress(self):
        time.sleep(1)
        st.write("")
        st.write("")
        st.write("")
        st.write("Sending results...")

    def show_server_response(self, response):
        time.sleep(1)
        st.header(response)

    def show_good_server_response_message(self, uploaded_object):
        time.sleep(1)
        st.write("")
        st.write(f"Uploaded the {uploaded_object}, got a good response back from the server.")
        st.write("")

    def show_connection_problem_response_message(self):
        time.sleep(1)
        st.write("")
        # st.write("Panel was not sent")
        # st.write("Looks like there's a connection problem. No response was received from the server.")
        # st.write("The system will send this panel (and all others) once the connection is restored.")
        st.write("")

    def show_bad_server_response_message(self, uploaded_object):
        time.sleep(1)
        st.write("")
        # st.write(f"Tried to upload the {uploaded_object}, got a bad response back from the server.")
        # st.write("This probably means a wrong serial number was used.")
        st.write("")

    def show_next_panel_test(self, move_to_next_panel):
        time.sleep(1)
        st.text("")
        st.text("")
        st.text("")
        if move_to_next_panel:
            st.text("You may continue to test the next panel.")
            self.show_next_panel_test_button()
        else:
            st.write("")
            #st.write("Do not continue, and contact the office for more information.")

    def show_next_panel_test_button(self):
        # clicked = st.button("Move on to test the next panel", key="next_panel_test",
        #                     on_click=self.set_show_next_panel_test_button_clicked)
        clicked = st.session_state.show_next_panel_test_button_clicked or \
                  st.button("Move on to test the next panel", key="next_panel_test",
                            on_click=self.set_show_next_panel_test_button_clicked)
        return clicked

    def show_restart_panel_button(self):
        # restart = st.session_state.show_restart_panel_button_clicked or \
        #           st.button("Restart Test", key="restart",
        #                     on_click=self.set_show_restart_panel_button_clicked)
        restart = st.button("Restart Test", key="restart",
                            on_click=self.set_show_restart_panel_button_clicked)

        return restart

    def reset_all_session_states(self):

        st.session_state.test_button_clicked = False
        st.session_state.send_results_button_clicked = False
        st.session_state.show_next_panel_test_button_clicked = False
        st.session_state.show_restart_panel_button_clicked = False
        st.session_state.serial_number_inserted = False
        st.session_state.results_table = None
        st.session_state.boards_list = None
        st.session_state.serial_number = None
        st.session_state.flashing_toggled = False
        st.session_state.slot_setup_toggled = False
        st.session_state.mode = 'with flash'
        st.session_state.number_of_boards = 9
        st.session_state.slot_setup = "all slots"
        st.session_state.number_of_boards_toggled = False



        #st.write(st.session_state)
        #Delete all the items in Session state
        # for key in st.session_state.keys():
        #    del st.session_state[key]
