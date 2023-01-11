#!/bin/bash

python3 /home/wld-hw/bluez-5.63/test/simple-agent &
cd /home/wld-hw/rpi_band_tester
#streamlit run main.py
firefox --kiosk | streamlit run main.py


