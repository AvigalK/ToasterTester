
# TODO - refactor main ,split functions


import random

#import Test_Extractor as te
import streamlit as st
import ToasterTester as tt
import GUI as gui
import Server as srv
from test_parameters import *
import time


if __name__ == '__main__':

    #'''

    start_time = time.time()
    #st.write(st.session_state)

    # create ToasterTester instance
    # if FAKE_BOARDS:
    #     toaster = tt.ToasterTester(NUM_OF_FAKE_BOARDS, WITH_GUI, FAKE_BOARDS)
    # else:
    # create GUI instance
    tester_screen = gui.Screen() if WITH_GUI else None
    tester_screen.show_restart_panel_button()
    if st.session_state.show_restart_panel_button_clicked:
        tester_screen.reset_all_session_states()
        st.experimental_memo.clear()
        st.experimental_singleton.clear()
        st.experimental_rerun()

    tester_screen.show_opening_message()
    col1, col2, col3 = st.columns(3)
    tester_screen.select_slot_setup(col1)
    tester_screen.toggle_flashing(col2)
    tester_screen.select_number_of_boards(col3)
    toaster = tt.ToasterTester(st.session_state.number_of_boards, WITH_GUI, FAKE_BOARDS)

    #tester_screen.toggle_flashing()
    # create Server instance
    server = srv.Server([], "server_buffer.json", "full_local_db.json")
    #tester_screen.show_insert_serial_number()

    # if tester_screen.toggle_flashing():


    # insert serial number for first board
    if st.session_state.mode != 'without flash':
        tester_screen.show_insert_serial_number()
        #tester_screen.show_first_serial_number()
    #     #st.write(st.session_state)

    # if WITH_GUI:
    #     tester_screen.show_first_serial_number()
    #     #tester_screen.show_if_serial_number_exists(server) # TODO - delete in the future (when we're working on several tester simultaneously)
    # else:
    #     st.session_state.serial_number = LAST_SN
    #     #st.session_state.serial_number = input("Serial Number: ")
    #     st.session_state.serial_number_inserted = True
    #     st.session_state.test_button_clicked = True
    #     st.session_state.send_results_button_clicked = False

    # test boards

    if tester_screen.show_run_test_button():

        # run tests on panel
        if not st.session_state.send_results_button_clicked and st.session_state.test_button_clicked:
            toaster.run_tests(tester_screen)
            st.session_state.results_table = toaster.boards_result_table
            st.session_state.boards_list = toaster.boards_list

        # show results on screen
        if WITH_GUI:
            tester_screen.show_results_message(toaster)
            tester_screen.show_results_damaged(toaster.num_of_damaged_boards, toaster.num_of_boards)
        # else:
        #     print(toaster.boards_result_table)
        #     st.session_state.send_results_button_clicked = True

        # send results to server
        #tester_screen.show_send_results_button()
        # print(f'show_send_results_button: {tester_screen.show_send_results_button()}')
        #print(f'1:{st.session_state.send_results_button_clicked}')
        if tester_screen.show_send_results_button():
            #print(f'2:{st.session_state.send_results_button_clicked}')
            if st.session_state.send_results_button_clicked:
                tester_screen.show_sending_results_in_progress()
                server.panel = st.session_state.boards_list
                #response = None

                # post request and get server's response
                # TODO - modify real and fake if's, plus in Server class
                #print(f' FAKE BOARDS: {FAKE_BOARDS}')

                responses = server.send_buffer(not FAKE_BOARDS)
                print(responses)
                #responses = server.send_buffer(True)
                #st.write(server.panel_json)
                connection_problem = False
                if (responses[0] or responses[1]) is None:
                    connection_problem = True
                #if FAKE_BOARDS:  # fake data
                #    connection_problem = random.choice([False])

                # show server response on screen
                uploaded_objects = ["board objects", "log files"]

                move_to_next_panel = True
                for i, response in enumerate(responses):
                    tester_screen.show_server_response(response)
                    if response in GOOD_STATUS_CODES:
                        tester_screen.show_good_server_response_message(uploaded_objects[i])
                        server.save_buffer_to_local_db()
                    elif connection_problem:
                        tester_screen.show_connection_problem_response_message()
                    else:
                        tester_screen.show_bad_server_response_message(uploaded_objects[i])
                        move_to_next_panel = False
                        server.clear_json_buffer()

                print(move_to_next_panel)
                # tester_screen.show_next_panel_test(move_to_next_panel)
                # if tester_screen.show_next_panel_test_button():
                #     tester_screen.reset_all_session_states()



    #print("--- %s seconds ---" % (time.time() - start_time))

    #'''
