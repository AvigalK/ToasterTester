import binascii
import subprocess
import serial
from pynrfjprog import APIError
import time
import sys
import os
import inspect
from snc_analyzer import *
from imu_analyzer import *
import threading
from bluepy import btle
import test_parameters

# ---------------------------------------------------------------
# handle arduino changing ports
import serial.tools.list_ports

ports = list(serial.tools.list_ports.comports())
for p in ports:
    if "Arduino Nano Every" in p.description:
        arduino_port = p


# ---------------------------------------------------------------

def setAdvStarted():
    global advStarted
    advStarted = True


class ArduinoCtl():

    def __init__(self, ser):
        self._ser = serial.Serial(arduino_port.device, 57600)
        time.sleep(1)

    def _write(self, command):
        return (self._ser.write(bytes(command, 'ascii')))

    def _read(self):
        return (self._ser.read(self._ser.in_waiting))

    def _getResponse(self):
        lines = self._read().splitlines()
        return lines[len(lines) - 1]

    def query(self, query):
        self._write(query)
        time.sleep(2)
        return self._getResponse()

    def _validateCmd(self, validation):
        return validation in self._read()

    def ValidatedQuery(self, cmd, validation):
        txt = self.query(cmd)
        print(str(txt).strip("'b"))
        return (validation in str(txt))


class pcbControl():
    def __init__(self, ser):
        self.dev = ArduinoCtl(ser)

    def setSNCCycle(self, n, cycle):
        self.dev._write("snc" + str(n) + " cycle " + str(cycle))
        time.sleep(2)
        txt = self.dev._read()
        print(txt)
        # return bytes("snc"+str(n)+" is on",'ascii') in txt

    def setSNCPhase(self, n, phase):
        self.dev._write("snc" + str(n) + " phase " + phase)
        time.sleep(2)
        txt = self.dev._read()
        print(txt)
        # return bytes("snc"+str(n)+" is on",'ascii') in txt

    def powerOnSNC(self, n):
        self.dev._write("snc" + str(n) + " power on")
        time.sleep(2)
        txt = self.dev._read()
        print(txt)
        return bytes("snc" + str(n) + " is on", 'ascii') in txt

    def powerOffSNC(self, n):
        self.dev._write("snc" + str(n) + " power off")
        time.sleep(2)
        txt = self.dev._read()
        print(txt)
        return bytes("snc" + str(n) + " is off", 'ascii') in txt

    def VibrationOn(self):
        self.dev._write("act power on")
        time.sleep(2)
        txt = self.dev._read()
        print(txt)

    #   return bytes("snc"+str(n)+" is on",'ascii') in txt

    def VibrationOff(self):
        self.dev._write("act power off")
        time.sleep(2)
        txt = self.dev._read()
        print(txt)
        return bytes("vibration is on", 'ascii') in txt

    def selectBoard(self, n):
        print(self.dev.ValidatedQuery("band select " + str(n), "switch address set to" + str(n)))

    def readVdig(self):
        return float(str(self.dev.query("Vdigital read")).strip("b'"))

    def led_indicate(self, n, status):
        self.dev._write(f'indicate {n} {status}')
        time.sleep(2)
        txt = self.dev._read()
        print(txt)

    def flasherRestart(self):
        # os.system("nrfjprog --reset")
        self.dev._write('Flasher dis')
        time.sleep(5)
        # input()
        self.dev._write('Flasher ena')
        #  input()
        time.sleep(2)
        txt = self.dev._read()
        print(txt)
        os.system("nrfjprog --reset")


class BLEScanFailed(Exception):
    pass


SNC_Data = []
IMU_Data = []


class HandleBle(btle.DefaultDelegate):
    _deviceName = None  # deviceName
    _cAddr = None
    _dev = None
    _peripheral = None
    _wld_services = None
    _char_config = None
    _char_snc = None
    _char_imu = None
    _snc_notify_handle = None
    _imu_notify_handle = None
    cmd_ena_snc = b'\x06\x01'
    cmd_dis_snc = b'\x06\x00'
    cmd_ena_imu = b'\x07\x00\x01'
    cmd_dis_imu = b'\x07\x00'
    cmd_ena_notif = b'\x01\x00'
    cmd_dis_notif = b'\x00\x00'
    cmd_shipmode = b'\xff\xad\xde'
    cmd_powerdown = b'\xf0\xef\xbe'
    cmd_clearbonds = b'\xfe'

    def __init__(cls):  # ,deviceName = None):
        btle.DefaultDelegate.__init__(cls)

    def scan(cls, sn, nTrials=10):

        __class__._deviceName = ("Mudra Band Black " + str(sn)).strip()
        # print (self._cAddr +" " + self._dev)
        print("Scanning for device " + __class__._deviceName)

        scanner = btle.Scanner().withDelegate(cls)
        tryal = 0
        while tryal < nTrials:
            try:
                dev = scanner.scan(1)
            except:
                time.sleep(0.5)
            if __class__._cAddr is not None:
                break
            else:
                tryal = tryal + 1
        if __class__._cAddr is None:
            raise BLEScanFailed
        # mac_addr = 'D4:34:E0:2B:FB:C3'
        print("device " + __class__._cAddr.addr + " found, connecting")

        subprocess.run(['expect', f'{os.getcwd()}/script.sh', __class__._cAddr.addr])

        while True:
            try:
                __class__._peripheral = btle.Peripheral(__class__._cAddr, "random", 0, "medium", 10000).withDelegate(
                    cls)
            #   __class__._peripheral.setMTU(123)
            #     __class__._peripheral.pair()
            except:
                pass
            else:
                break
        time.sleep(2)
        while True:
            try:
                time.sleep(0.5)
                cls.flash()

                wld_services = __class__._peripheral.getServiceByUUID(0xfff0)
                chars = wld_services.getCharacteristics()
            except(APIError.APIError):

                pass
            else:
                break
        cls.flash()
        wld_services = __class__._peripheral.getServiceByUUID(0xfff0)
        cls.flash()

        chars = wld_services.getCharacteristics()
        __class__._char_config = chars[0]
        __class__._char_snc = chars[3]
        __class__._char_imu = chars[4]
        __class__._snc_notify_handle = __class__._char_snc.getHandle() + 1
        __class__._imu_notify_handle = __class__._char_imu.getHandle() + 1

    def startSNC(cls):
        # enable notifications
        cls.flash()
        __class__._peripheral.writeCharacteristic(__class__._snc_notify_handle, __class__.cmd_ena_notif)
        # enable SNC configuration
        cls.flash()
        __class__._char_config.write(__class__.cmd_ena_snc)
        # todo: add code for start thred
        __class__._peripheral.waitForNotifications(30)

    def stopSNC(cls):

        # disable SNC configuration
        # cls.flash()
        __class__._char_config.write(__class__.cmd_dis_snc)
        # disable notifications
        # cls.flash()
        __class__._peripheral.writeCharacteristic(__class__._snc_notify_handle, __class__.cmd_dis_notif)
        # todo: add code for stop thred

    def startIMU(cls):
        # enable notifications
        cls.flash()

        __class__._peripheral.writeCharacteristic(__class__._imu_notify_handle, __class__.cmd_ena_notif)
        # enable SNC configuration
        cls.flash()
        __class__._char_config.write(__class__.cmd_ena_imu)
        # todo: add code for start thred
        __class__._peripheral.waitForNotifications(30)

    def stopIMU(cls):

        # disable SNC configuration
        __class__._char_config.write(__class__.cmd_dis_imu)
        # disable notifications

        __class__._peripheral.writeCharacteristic(__class__._imu_notify_handle, __class__.cmd_dis_notif)
        # todo: add code for stop thred

    def flash(cls):
        try:
            __class__._peripheral._getResp("", 1)
        except:
            pass

    def unpair(cls):

        cls.flash()
        __class__._char_config.write(__class__.cmd_shipmode)
        args = "bluetoothctl remove " + str(__class__._cAddr.addr)
        os.system(args)

    def sendCmd(cls, cmd):
        __class__._peripheral._mgmtCmd(cmd)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        # print ("handling discovery"+ __class__._deviceName )
        if __class__._deviceName is None:
            print("no device requested")
            return
        deviceName = dev.getValueText(9)
        if __class__._deviceName is not None:
            if deviceName is not None:

                print(f'looking for {__class__._deviceName}')
                print(f'device found {deviceName}')

            if __class__._deviceName == deviceName:
                # print ("found device "+_deviceName + " "+ dev.addr )
                __class__._cAddr = dev

                raise btle.devFound()

    def handleNotification(self, hnd, data):

        print("handle notifications")
        if hnd == __class__._char_snc.getHandle():
            SNC_Data.append(data)
        elif hnd == __class__._char_imu.getHandle():
            IMU_Data.append(data)

        # print (data)


class FlashCtl:
    def __init__(self):
        from pynrfjprog import LowLevel
        self._api = LowLevel.API('NRF52')
        self._close_event = None
        self._reader_thread = None

    def connect(self):
        try:
            self._api.open()
            self._api.connect_to_emu_without_snr(4000)
        except(APIError.APIError):
            self.__del__()

    def disconnect(self):
        try:
            self._api.close()
        except(APIError.APIError):
            self.__del__()

    def flashBoard(self, sn=None):

        if sn:
            try:
                program_file = '6.0.5.49.hex' #'Tester.hex'
                os.system("nrfjprog --recover")
                time.sleep(1)
                self._api.erase_all()
                # print(1)
                self._api.program_file(f'{os.getcwd()}/{program_file}')
                # print(2)
                self._api.verify_file(f'{os.getcwd()}/{program_file}')
                # print(3)
                self._api.write_u32(0x10001080, sn, True)
                self._api.write_u32(0x100010FC, 0x00000100, True)
                time.sleep(5)
                os.system("nrfjprog --reset")
                os.system("nrfjprog --run")
                # self._api.sys_reset()
                time.sleep(2)
                print("device restarted\n")

            except(APIError.APIError) as e:
                err = str(e)
                err = err[err.find('DLL: ') + 5:]
                print(f'Error :{err}')
                self.__del__()
                raise e

    def printSn(self):
        try:
            print("device serial " + str(self._api.read_u32(0x10001080)))
        except(APIError.APIError):
            print("API ERROR")
            self.__del__()

    def readSn(self):
        try:
            sn = self._api.read_u32(0x10001080)
        except(APIError.APIError):
            sn = None
            print("API ERROR")
            self.__del__()
        return sn

    def restart(self):
        try:
            self._api.sys_reset()
        except(APIError.APIError):
            self.__del__()

    def _reader(self):

        print("reader started")
        self._api.go()
        # os.system("nrfjprog --run")
        flag = 0
        BLOCK_SIZE = 512
        rtt_data = ""
        global last_line

        # out_file = open(f'rtt_log_{self._api.read_u32(0x10001080)}.txt', "w+")

        test_rtt_input = open(f"{test_parameters.main_dir}/rtt_log_tested_{self._api.read_u32(0x10001080)}.txt", "w+")

        # sys.stdout = open(f'rtt_log_{self._api.read_u32(0x10001080)}.txt', 'w+')
        while not self._close_event.is_set():
            try:
                rtt_data = self._api.rtt_read(0, BLOCK_SIZE)
                #   if not "\r\n" in rtt_data:
                #      continue
                if "GO_TO_SLEEP" in rtt_data:
                    self._api.go()
                    # os.system("nrfjprog --reset")
                    time.sleep(3)
                    # os.system("nrfjprog --run")

            except:
                self.__del__()

            if rtt_data == "" or type(rtt_data) == int:
                time.sleep(0.1)

                continue

            rtt_data = rtt_data.rstrip("\r\n")
            for s in rtt_data.splitlines():
                if s.strip() == "":
                    continue

                sys.stdout.write(s)

                # out_file.write(f'{s}\n')
                if not flag:
                    test_rtt_input.write(f'{s}\n')

                if "battery capacity" in s:
                    time.sleep(5)
                    setAdvStarted()
                    print(
                        "************************************** Advertising discovered **********************************")
                    test_rtt_input.close()

                    flag = 1

                sys.stdout.write('\n')
                sys.stdout.flush()
                last_line = rtt_data
                rtt_data = ""

    def killThread(self):
        if self._close_event is not None:
            self._close_event.set()

    def runRtt(self):
        print("runRtt: ")
        # self._api.go()
        os.system("nrfjprog --run")
        try:
            self._api.rtt_start()
            # Wait for RTT to find control block etc.
            time.sleep(0.5)
            # os.system("nrfjprog --run")
            while not self._api.rtt_is_control_block_found():
                self._api.rtt_stop()
                time.sleep(0.5)
                self._api.rtt_start()
                time.sleep(0.5)

            # while not self._api.rtt_is_control_block_found():
            #     time.sleep(10)
            #     os.system("nrfjprog --run")
            #     time.sleep(10)

            print("_reader init")
            # os.system("nrfjprog --run")
            self._close_event = threading.Event()
            self._close_event.clear()
            self._reader_thread = threading.Thread(target=self._reader)
            self._reader_thread.start()


        except(APIError.APIError) as e:
            print(e)
            self.__del__()
            raise e

    def __del__(self):
        self.disconnect()


def getNextSN():
    return 0x09


class FlashActions():
    def __init__(self):
        self._fc = FlashCtl()
        self._fc.connect()

    def flashDevice(self, sn):
        print("flashing device " + str(sn))

        try:
            self._fc.flashBoard(sn)
            print("Device Flashed")
        except APIError.APIError as e:
            print("Device was not flashed")
            raise e

    def runDevice(self):
        # self._fc.restart()
        print("running device")

        try:
            self._fc.printSn()
            print("Running RTT")
            self._fc.runRtt()
        except APIError as e:
            print(e)
            raise e

    def getSerial(self):
        return self._fc.readSn()

    def reset(self):
        self._fc.restart()

    @staticmethod
    def closeThreads(self):
        self._fc.killThread()
        print("done reading")


def report(subject, content):
    print("Report >>  " + subject + "," + content + "\n")


# ---------------------------------------------------------------
""" main function that updates board objects """




def testBoard(board, nPcb, serial_num, pcb, mode, screen):
    # helper functions:

    def initSNCinject():
        # SNC injection initied to 200hx ( flat signal on SNC)
        # pcb.setSNCPhase(1, 'on')
        # pcb.setSNCPhase(2, 'on')
        # pcb.setSNCPhase(3, 'on')

        pcb.setSNCCycle(1, 1000000 / 200)
        pcb.powerOnSNC(1)

        pcb.setSNCCycle(2, 1000000 / 200)
        pcb.powerOnSNC(2)

        pcb.setSNCCycle(3, 1000000 / 200)
        pcb.powerOnSNC(3)

    # ---------------------------------------------------------------

    def testIMU():
        #   test IMU signals
        lp.startIMU()
        time.sleep(10)
        #pcb.VibrationOn()
        time.sleep(2)  # extra
        time.sleep(3)
        pcb.VibrationOff()
        time.sleep(3)
        lp.stopIMU()

        f = open(f"{test_parameters.main_dir}IMU_{serial_num}.txt", "w+")
        f.write(str(list(map(binascii.b2a_hex, IMU_Data))))

        f.close()

        imu, res = imu_analyzer(f'{test_parameters.main_dir}IMU_{serial_num}.txt', serial_num)
        print(f"imu_res = {res}")

        return res

    # ---------------------------------------------------------------
    # def testSNC():
    #     #   test SNC signals
    #     initSNCinject()
    #     print("recording when all channels off")
    #     lp.startSNC()
    #     time.sleep(10)
    #     lp.stopSNC()
    #     #
    #     # print("recording when ch1 50hz sqr wave")
    #     # pcb.setSNCCycle(1, 1000000 / 200)
    #     # pcb.setSNCCycle(2, 1000000 / 200)
    #     # pcb.setSNCCycle(3, 1000000 / 200)
    #     #
    #     # lp.startSNC()
    #     # time.sleep(1)
    #     # lp.stopSNC()
    #
    #     # lp.startSNC()
    #     # time.sleep(1)
    #     # lp.stopSNC()
    #     # pcb.setSNCCycle(1, 1000000 / 200)
    #     # pcb.setSNCCycle(2, 1000000 / 200)
    #     # pcb.setSNCCycle(3, 1000000 / 200)
    #     # lp.startSNC()
    #     # time.sleep(1)
    #     # lp.stopSNC()
    #
    #
    #     f = open(f"{test_parameters.main_dir}SNC_{serial_num}.txt", "w+")
    #     f.write(str(list(map(binascii.b2a_hex, SNC_Data))))
    #     f.close()
    #
    #     snc, res, snc0_test_res, snc1_test_res, snc2_test_res = snc_analyzer(
    #         f"{test_parameters.main_dir}SNC_{serial_num}.txt", serial_num)
    #     print(f"snc0_res = {snc0_test_res}")
    #     print(f"snc1_res = {snc1_test_res}")
    #     print(f"snc2_res = {snc2_test_res}")
    #     return res

    def testSNC():

        #   test SNC signals
        initSNCinject()
        print("recording when all channels off")
        # time.sleep(1)
        lp.startSNC()
        time.sleep(5)
        lp.stopSNC()
        pcb.setSNCCycle(1, 1000000 / 120)
        time.sleep(1)
        lp.startSNC()
        time.sleep(5)
        lp.stopSNC()

        pcb.setSNCCycle(1, 1000000 / 70)
        time.sleep(1)
        lp.startSNC()
        time.sleep(5)
        lp.stopSNC()

        # #   test SNC signals
        # initSNCinject()
        # print("recording when all channels off")
        # #time.sleep(1)
        # lp.startSNC()
        # time.sleep(1)
        # lp.stopSNC()

        # print("recording when ch1 50hz sqr wave")
        # # pcb.setSNCCycle(1, 1000000 / 50)
        # pcb.setSNCCycle(1, 1000000 / 300)
        # #time.sleep(1)
        # lp.startSNC()
        # time.sleep(1)
        # lp.stopSNC()
        #
        # print("recording when ch2 50hz sqr wave")
        # pcb.setSNCCycle(1, 1000000 / 200)
        # # pcb.setSNCCycle(2, 1000000 / 50)
        # pcb.setSNCCycle(2, 1000000 / 300)
        # #time.sleep(1)
        #
        # lp.startSNC()
        # time.sleep(1)
        # lp.stopSNC()
        #
        # print("recording when ch3 50hz sqr wave")
        # pcb.setSNCCycle(2, 1000000 / 200)
        # # pcb.setSNCCycle(3, 1000000 / 50)
        # pcb.setSNCCycle(3, 1000000 / 300)
        # #time.sleep(1)
        # lp.startSNC()
        # time.sleep(1)
        # lp.stopSNC()
        #
        # print("turning sqr wave off")
        # pcb.setSNCCycle(3, 1000000 / 200)
        # #time.sleep(1)
        # lp.startSNC()
        # time.sleep(1)
        # lp.stopSNC()

        f = open(f"{test_parameters.main_dir}SNC_{serial_num}.txt", "w+")
        f.write(str(list(map(binascii.b2a_hex, SNC_Data))))
        f.close()

        snc, res, snc0_test_res, snc1_test_res, snc2_test_res = snc_analyzer(
            f"{test_parameters.main_dir}SNC_{serial_num}.txt", serial_num)
        print(f"snc0_res = {snc0_test_res}")
        print(f"snc1_res = {snc1_test_res}")
        print(f"snc2_res = {snc2_test_res}")
        return res

    # ---------------------------------------------------------------

    # init
    start_time = time.time()
    os.system("rfkill block bluetooth")
    time.sleep(0.5)
    os.system("rfkill unblock bluetooth")
    # initialize the arduino
    # ser = serial.Serial(arduino_port.device, 57600)
    # pcb = pcbControl(ser)

    # ---------------------------------------------------------------
    # Check contacts between bands and testing hardware by reading voltage on a non-connected pin of the switch
    # TODO uncomment
    print("Checking contacts...")
    pcb.selectBoard(10)
    voltage = pcb.readVdig()
    while voltage > 0.5:
        input("BAD CONTACTS - please check that all the bands are connected properly")
        voltage = pcb.readVdig()
    print("Bands are connected, starting test...")

    # ---------------------------------------------------------------

    print("new flasher session")

    import streamlit as st
    placeholder = st.empty()
    progress_bar = screen.show_progress_bar(placeholder)

    lp = HandleBle()

    sn = board.serial_number
    #sn = 587

    pcb.selectBoard(nPcb)  # nPcb
    pcb.flasherRestart()
    fc = FlashActions()
    pcb.led_indicate(nPcb, 'test')  # turn on yellow LED to indicate start testing
    # Test VDIG
    tryals = 0
    while tryals < 5:
        try:
            Vdig = pcb.readVdig()
            break
        except:
            pcb.flasherRestart()
            print("check band connections")
            tryals += 1

    if Vdig < 1.0:  # TODO - change to 1.7?
        board.vdig = [Vdig, False]
        '''
        print("Low Vdigital! cant flash board - aborting test \n check that the board attached correctly")
        report("Vdigital", "Fail")
        '''
        pcb.led_indicate(nPcb, 'fail')
        screen.update_progress_bar(7, progress_bar, placeholder)
        return board
    else:
        board.vdig = [Vdig, True]

    screen.update_progress_bar(1, progress_bar, placeholder)
    # Test Flash Burn
    if mode == 'with flash':
        try:
            fc.flashDevice(serial_num)
            os.system("nrfjprog --reset")

        except APIError.APIError as e:
            print(e)
            board.burn = [False]
            pcb.led_indicate(nPcb, 'fail')
            screen.update_progress_bar(7, progress_bar, placeholder)
            return board
    screen.update_progress_bar(2, progress_bar, placeholder)
    Vdig = pcb.readVdig()
    if Vdig > 1.6:  # change closer to 3.5?
        print("Vdigital ok")
        board.burn = [True]
    else:
        print("Low Vdigital!" + str(pcb.readVdig()))
        # time.sleep(5)
        board.burn = [False]
        pcb.led_indicate(nPcb, 'fail')
        screen.update_progress_bar(7, progress_bar, placeholder)
        return board
    screen.update_progress_bar(3, progress_bar, placeholder)
    # Test RTT Inits
    global advStarted
    advStarted = False

    tryals = 0
    while tryals < 5:
        if tryals > 0:
            # fc.reset()
            fc = FlashActions()
            advStarted = False
        start_time_rtt = time.time()
        print(f"run number {tryals}")
        try:
            fc.runDevice()
        except:
            pcb.led_indicate(nPcb, 'fail')
            board.is_damaged = True
            screen.update_progress_bar(7, progress_bar, placeholder)
            return board

        while advStarted == False:

            if time.time() - start_time_rtt > 60:
                os.system("nrfjprog --run")
                global last_line
                # print(last_line)
                # pcb.flasherRestart()
                # input("should restart?")
                # os.system("nrfjprog --run")
                break
            pass

        if advStarted == True:
            break

        tryals += 1
        if tryals == 4:
            board.is_damaged = True
            pcb.led_indicate(nPcb, 'fail')
            fc.closeThreads(fc)
            screen.update_progress_bar(7, progress_bar, placeholder)
            return board
    screen.update_progress_bar(4, progress_bar, placeholder)
    # # Test Bluetooth
    # print("\n****************** Advertising Started****************")
    # tryBT = 0
    #
    # while tryBT < 4 and board.is_damaged != True:
    #
    #     try:
    #         lp.scan(sn)
    #         board.bluetooth = [True]
    #         break
    #
    #
    #     except BLEScanFailed as e:
    #         board.bluetooth = [False]
    #         tryBT += 1
    # if tryBT == 3:
    #     board.is_damaged = True
    #     pcb.led_indicate(nPcb, 'fail')
    #     screen.update_progress_bar(7, progress_bar, placeholder)
    #     return board
    # screen.update_progress_bar(5, progress_bar, placeholder)
    # print("##################start IMU test##############")
    # tryIMU = 0
    # imu_res = False
    # while tryIMU < 4 and board.is_damaged != True:
    #     try:
    #         imu_res = testIMU()
    #         break
    #     except:
    #         print("disconnected from Bluetooth during imu test, trying again..")
    #         IMU_Data.clear()
    #         tryIMU += 1
    #         os.system("rfkill block bluetooth")
    #         time.sleep(0.5)
    #         os.system("rfkill unblock bluetooth")
    #         time.sleep(0.5)
    #         try:
    #             lp.scan(sn)
    #         except:
    #             pass
    #             # os.system("rfkill block bluetooth")
    #             # time.sleep(0.5)
    #             # os.system("rfkill unblock bluetooth")
    #             # time.sleep(0.5)
    #
    # if tryIMU == 3:
    #     board.is_damaged = True
    #     pcb.led_indicate(nPcb, 'fail')
    #     screen.update_progress_bar(7, progress_bar, placeholder)
    #     return board
    # screen.update_progress_bar(6, progress_bar, placeholder)
    # print("##################start SNC test##############")
    # trySNC = 0
    # snc_res = False
    # while trySNC < 4 and board.is_damaged != True:
    #
    #     try:
    #         snc_res = testSNC()
    #         break
    #     except Exception as e:
    #         print(e)
    #         print("disconnected from Bluetooth during snc test, trying again..")
    #         SNC_Data.clear()
    #         trySNC += 1
    #         os.system("rfkill block bluetooth")
    #         time.sleep(0.5)
    #         os.system("rfkill unblock bluetooth")
    #         time.sleep(0.5)
    #
    #     try:
    #         lp.scan(sn)
    #     except:
    #         pass
    #         # os.system("rfkill block bluetooth")
    #         # time.sleep(0.5)
    #         # os.system("rfkill unblock bluetooth")
    #         # time.sleep(0.5)
    #
    # if trySNC == 3:
    #     board.is_damaged = True
    #     pcb.led_indicate(nPcb, 'fail')
    #     screen.update_progress_bar(7, progress_bar, placeholder)
    #     return board
    #
    # # testSNC()
    # snc_f = open(f"{test_parameters.main_dir}concated_signal_SNC_{board.serial_number}.csv", "r")
    # imu_f = open(f"{test_parameters.main_dir}concated_signal_{board.serial_number}.csv", "r")
    #
    # output_snc = snc_f.readline()
    # output_imu = imu_f.readline()
    # snc_f.seek(0, 0)
    # imu_f.seek(0, 0)
    #
    # if snc_res:
    #     board.snc = [True]
    # else:
    #     board.is_damaged = True
    #     board.snc = [False]
    #     pcb.led_indicate(nPcb, 'fail')
    #
    # if imu_res:
    #     board.imu = [True]
    # else:
    #     board.is_damaged = True
    #     board.imu = [False]
    #     pcb.led_indicate(nPcb, 'fail')
    #
    # # finalizing tests on board and update LEDs
    # print("killing threads...")
    # fc.closeThreads(fc)
    # time.sleep(10)
    # # print(board.extractor.get_relevant_lines())
    # # print(board.extractor.test)
    # rtt_attributes = board.extractor.test()
    # # print(f'final attr for leds: {rtt_attributes}')
    # if False in rtt_attributes[0:1] or board.is_damaged:
    #     pcb.led_indicate(nPcb, 'fail')
    # else:
    #     pcb.led_indicate(nPcb, 'pass')
    # try:
    #     board.current = rtt_attributes[0]
    #     board.battery_voltage = rtt_attributes[1]
    # except:
    #     print(
    #         f"Something went wrong with the rtt log parsing for this board, please test board with serial {sn} again!")
    # screen.update_progress_bar(7, progress_bar, placeholder)
    # print("--- %s seconds ---" % (time.time() - start_time))
    # SNC_Data.clear()
    # IMU_Data.clear()

    return board
