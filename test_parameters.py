
# GUI Parameters
WITH_GUI = True

# Test Parameters
FAKE_BOARDS = False
NUM_OF_FAKE_BOARDS = 3
NUM_OF_REAL_BOARDS = 9  # TODO - change from 1 to 9 to work on board/full panel

MAX_CHARS_SN = 100  # TODO - change it according to the convention we decide on
LAST_SN = 0x00

# Server Parameters
STATUS_CODES = [200, 201, 202, 204, 400, 401, 404, 415, 422, 500]
GOOD_STATUS_CODES = [200, 201, 202, 204]
BAD_STATUS_CODES = [400, 401, 404, 415, 422, 500]

# File paths
#main_dir = '/home/wld-hw/rpi_band_tester/output_files/'
import os
main_dir = f'{os.getcwd()}/output_files/'

