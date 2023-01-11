# TODO - change from hardcoded
import test_parameters

TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJJZCI6IjYyNmY3ZmJkMjliNWM2MjZmMzcwNWQzOSIsInJvbGVzIjoiUk9MRV9BRE1JTiIsImlhdCI6MTY1ODMyMzg2MSwiZXhwIjoxODE2MDAzODYxfQ.OH9Dglh368P1GI3RvsX6Y1fV_d6JSygVWACXH6X1IZc"

import random
import requests as rq
import json
from test_parameters import *
import streamlit as st  # TODO - delete this


# import string

class APIBoard:

    def __init__(self, board):
        self.serial_number = board.serial_number
        self.is_damaged = board.is_damaged
        self.vdig_value = board.vdig[0]
        self.vdig_is_pass = board.vdig[1]
        self.burn_is_pass = board.burn[0]
        self.current_value = board.current[1]
        self.current_is_pass = board.current[2]
        self.battery_voltage_value = board.battery_voltage[1]
        self.battery_voltage_is_pass = board.battery_voltage[2]
        self.bluetooth = board.bluetooth[0]
        self.imu = board.imu[0]
        self.snc = board.snc[0]
        # TODO - add attributes if needed

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class Server:

    def __init__(self, boards_list, buffer, local_db):
        self.panel = boards_list
        self.json_panel_to_save = self.convert_panel_to_json(boards_list)[0]
        self.json_panel_to_send = self.convert_panel_to_json(boards_list)[1]
        self.json_server_buffer = buffer
        self.json_full_panel_db = local_db

    # Creates an array of 9 JSONs for a panel
    def convert_panel_to_json(self, boards_list):
        boards_list_json = []
        for i, board in enumerate(boards_list):
            api_board = APIBoard(board)
            boards_list_json.append(api_board.to_json())
            #print(type(boards_list_json[i]))
        trimmed_boards_list = self.trim_json(boards_list_json)
        trimmed_boards_list_json = self.list_to_json_array(trimmed_boards_list)
        #print("trimmed_boards_list_json:", trimmed_boards_list_json)
        return [boards_list_json, trimmed_boards_list_json]

    # TODO - finish implementation
    # Trims json ' and \n for sending
    def trim_json(self, json_to_trim):
        # print(type(json_to_trim[0]))
        trimmed_json = []
        for i in range(len(json_to_trim)):
            trimmed_json.append(json_to_trim[i].replace("\n", ""))
            # print("trimmed" + trimmed_json[i])
        return trimmed_json

    # TODO - find an existing implementation in json library
    # generates a json array
    def list_to_json_array(self, board_list):
        json_array = "["
        for board_json in board_list:
            json_array += board_json
        json_array += "]"
        json_array = json_array.replace("}{", "},{")
        #print("json_array:", json_array)
        return json_array

    # TODO - work on function
    # The code for sending the JSONs array to server
    def send_buffer(self, to_send):  # TODO - right now - send the panel tested, not the buffer
        self.json_panel_to_save = self.convert_panel_to_json(self.panel)[0]
        self.json_panel_to_send = self.convert_panel_to_json(self.panel)[1]
        self.save_panel_to_buffer()
        if to_send:

            # send panel
            set_pcb_api_url = "https://inventory.mudra-server.com/api/v1/inventory/setPCB"
            set_pcb_headers = {"Content-Type": "application/json", "Authorization": f"Bearer {TOKEN}"}
            # print(self.json_panel_to_send)
            # TODO - change to data=self.json_server_buffer
            if st.session_state.serial_number is not None:
                set_pcb_response = rq.post(set_pcb_api_url, data=self.json_panel_to_send, headers=set_pcb_headers)
            else:
                set_pcb_response = None

                # send log_files
            upload_log_api_url = "https://inventory.mudra-server.com/api/v1/inventory/uploadLog"
            uploaded = []
            latest = None
            # log_file_to_send = None
            for i in range(len(self.panel)):
                latest_time = 0
                #print(f'serial: {st.session_state.serial_number}')
                #s = st.session_state.serial_number.split(' ')
                for file in os.listdir(test_parameters.main_dir):
                    if st.session_state.serial_number != "":
                        split = st.session_state.serial_number.split(' ') if st.session_state.mode == 'with flash' else st.session_state.serial_number
                        #print(f'split: {split[i]}')
                        if split is not None:
                            sn = split[i] if type(split) == list else int(split)
                        else:
                            sn = None
                        # input(sn
                        if file.startswith(f"rtt_log_{sn}_"):
                            raw_name = file.replace(f"rtt_log_{sn}_", "").replace(".txt", "").replace("_", "").replace(
                                ":", "")
                            if int(raw_name) > latest_time:
                                latest = file
                                latest_time = int(raw_name)


                if latest not in uploaded and latest is not None:
                    log_file_to_send = latest
                    uploaded.append(latest)
                else:
                    log_file_to_send = None

                    # log_file_to_send = file
                if st.session_state.serial_number != None :
                    print(f"log path to send: {log_file_to_send}")
                    # log_file_to_send = f"{test_parameters.main_dir}/rtt_log_{int(st.session_state.serial_number.split(' ')[i])}.txt"
                    upload_log_headers = {
                        "Authorization": f"Bearer {TOKEN}"}  # TODO - change content-type to txt - "Content-Type": "application/json",
                    with open(f"{test_parameters.main_dir}{log_file_to_send}", 'rb') as f:
                        files = {"file": (log_file_to_send, f)}
                        upload_log_response = rq.post(upload_log_api_url, files=files, headers=upload_log_headers)
                    # print(upload_log_response)



            '''
            
            # first try
            
            #file_list = ['rtt_log_1.txt', 'rtt_log_2.txt', 'rtt_log_3.txt']
            #files = [eval(f'("inline", open("{file}", "rb"))') for file in file_list]
            #files = [open('rtt_log_1.txt', "rb"), open('rtt_log_2.txt', "rb"), open('rtt_log_3.txt', "rb")]
            files = open('rtt_log_1.txt', "rb")
            print(files)
            upload_log_response = rq.post(upload_log_api_url, files=files, headers=upload_log_headers)
            
            # sceond try
            log_files = {}
            open_logs = [None] * len(self.panel)
            for i in range(len(self.panel)): # TODO - change to serial number
                file = f"rtt_log_{i+1}.txt"
                open_logs[i] = open(file, 'rb')
                log_tuple = (file, open_logs[i])
                log_tuple = open_logs[i]
                log_files[f"log_file_{i+1}"] = log_tuple
            print(log_files)
            upload_log_response = rq.post(upload_log_api_url, files=log_files, headers=upload_log_headers)
            for i in range(len(open_logs)):
                open_logs[i].close()
            print(upload_log_response)
            '''
            try:
                upload_log_response
            except NameError:
                upload_log_response = None

            pcb_res = set_pcb_response.status_code if set_pcb_response is not None else None
            up_log_res = upload_log_response.status_code if upload_log_response is not None else None
            res = pcb_res, up_log_res

            return res  # TODO - notice that this is only status_code for last log_file
        else:
            # return random.choice(STATUS_CODES)
            # print(self.json_server_buffer)
            # print(self.json_panel_to_save)
            # print(self.json_panel_to_send)
            return [200, 200]

    # TODO - think if this function is needed, delete it otherwise
    def save_panel_to_buffer(self):
        with open(self.json_server_buffer, 'a') as json_buffer:
            # st.write("what is saved:")  # TODO - delete this
            for i in self.json_panel_to_save:
                # st.write(i)  # TODO - delete this
                json_buffer.write(i)

    def save_buffer_to_local_db(self):
        with open(self.json_full_panel_db, 'a') as json_local_db:
            with open(self.json_server_buffer, 'r') as json_buffer:
                for line in json_buffer:
                    json_local_db.write(line)
        self.clear_json_buffer()

    def clear_json_buffer(self):
        with open(self.json_server_buffer, 'r+') as json_buffer:
            json_buffer.truncate(0)

    def check_if_serial_number_exists(self, serial_number):
        url = "https://inventory.mudra-server.com/api/v1/inventory/getPCB"
        headers = {"Authorization": f"Bearer {TOKEN}"}
        response = rq.get(url, params={"itemId": f"{serial_number}"}, headers=headers)
        return True if response.status_code == 200 else False
