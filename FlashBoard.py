import binascii
import argparse
import subprocess
import serial
from pynrfjprog import APIError
import time
import sys
import os
import inspect
from snc_analyzer import *
from imu_analyzer import *
from client_server_utils import *

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()) + "/bluepy/bluepy/"))
sys.path.insert(0, currentdir)
from bluepy import btle


class ArduinoCtl():

    def __init__(self, ser):
        self._ser = serial.Serial("/dev/ttyACM0", 57600)
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
    cmd_ena_imu = b'\x07\x01'
    cmd_dis_imu = b'\x07\x00'
    cmd_ena_notif = b'\x01\x00'
    cmd_dis_notif = b'\x00\x00'
    cmd_shipmode = b'\xff\xad\xde'
    cmd_powerdown = b'\xf0\xef\xbe'
    cmd_clearbonds = b'\xfe'

    def __init__(cls):  # ,deviceName = None):
        btle.DefaultDelegate.__init__(cls)

    #  self._deviceName = None #deviceName
    #  self._cAddr = None
    #  self._dev = None
    #  self._peripheral = None

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
                print(".")
                tryal = tryal + 1
        if __class__._cAddr is None:
            raise BLEScanFailed

        print("device found, connecting")
        while True:
            try:
                __class__._peripheral = btle.Peripheral(__class__._cAddr, "random", 0, "medium", 10000).withDelegate(
                    cls)
                __class__._peripheral.setMTU(247)
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
                # except(BrokenPipeError):

                # time.sleep(0.5)
                # cls.flash()
                # wld_services = __class__._peripheral.getServiceByUUID(0xfff0)
                # cls.flash()
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

    #       while True:
    #           try:
    #               #todo: add code for start thred
    #               __class__._peripheral.waitForNotifications(30)
    #           except:
    #               pass
    #           else:
    #               break

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
            # print (_deviceName)
            if __class__._deviceName == deviceName:
                # print ("found device "+_deviceName + " "+ dev.addr )
                __class__._cAddr = dev
                raise btle.devFound()

    def handleNotification(self, hnd, data):
        print("handle notifications")
        if hnd == __class__._char_snc.getHandle():
            SNC_Data.append(data)
            print("snc")
        elif hnd == __class__._char_imu.getHandle():
            IMU_Data.append(data)

        # print (data)


class FlashCtl:
    def __init__(self):
        from pynrfjprog import LowLevel
        self._api = LowLevel.API('NRF52')

    def connect(self):
        try:
            self._api.open()
            self._api.connect_to_emu_without_snr(4000)
        except(APIError.APIError):
            self.__del__()
            return -1
            # TODO
            # return APIError.APIError

    def disconnect(self):
        try:
            self._api.close()
        except(APIError.APIError):
            self.__del__()

    def flashBoard(self, sn=None):
        if sn:
            try:
                self._api.erase_all()
                self._api.program_file('latest.hex')
                self._api.write_u32(0x10001080, sn, True)
                self._api.write_u32(0x100010FC, 0x00000100, True)
                self._api.go()
            except(APIError.APIError):
                self.__del__()
                return -1
                # TODO
                # return APIError.APIError

    def printSn(self):
        try:
            print("device serial " + str(self._api.read_u32(0x10001080)))
        except(APIError.APIError):
            self.__del__()

    def restart(self):
        try:
            self._api.sys_reset()
        except(APIError.APIError):
            self.__del__()

    def runRtt(self):
        try:
            self._api.rtt_start()
            # Wait for RTT to find control block etc.

            while not self._api.rtt_is_control_block_found():
                #  logging.info("Looking for RTT control block...")
                self._api.rtt_stop()
                time.sleep(0.5)
                self._api.rtt_start()
                time.sleep(0.5)
        except(APIError.APIError):
            self.__del__()

    def PrintRttData(self, board, output):
        try:
            BLOCK_SIZE = 512
            rtt_data = self._api.rtt_read(0, BLOCK_SIZE)
            if rtt_data == "" or type(rtt_data) == int:
                time.sleep(0.1)
                return 1

            if output == 'file':
                with open(board.extractor.infile, "a") as rtt_log_file:
                    # Append rtt_data at the end of file
                    rtt_log_file.write(rtt_data)
            else:
                print(rtt_data)

            if "GO_TO_SLEEP" in rtt_data:
                self._api.go()
            return 0

        except(APIError.APIError):
            self.__del__()

    def __del__(self):
        self.disconnect()


def getNextSN():
    return 0x09


class FlashActions():
    def __init__(self):
        self._fc = FlashCtl()

    def flashDevice(self, sn):
        print("flashing device " + str(sn))
        self._fc.connect()
        self._fc.flashBoard(sn)
        print("Device Flashed")

    def runDevice(self, board):

        print("running device")
        self._fc.printSn()
        try:
            self._fc.runRtt()
            #self._fc.PrintRttData()
            self._fc.PrintRttData(board, 'file')
        # while True:
        #    while True:
        #        if fc.PrintRttData() == 1:
        #            time.sleep(0.1)
        #            continue
        except:
            pass
        finally:
            pass


def testBoard(board, nPcb, log_file, attributes):
    # helper functions:

    def initSNCinject():
        # SNC injection initied to 200hx ( flat signal on SNC)

        pcb.setSNCCycle(0, 1000000 / 200)
        pcb.powerOnSNC(0)

        pcb.setSNCCycle(1, 1000000 / 200)
        pcb.powerOnSNC(1)

        pcb.setSNCCycle(2, 1000000 / 200)
        pcb.powerOnSNC(2)

    # --------------------------------------------

    def testIMU():
        #   test IMU signals
        lp.startIMU()
        lp.stopIMU()

        pcb.VibrationOn()

        lp.startIMU()
        time.sleep(1)
        lp.stopIMU()

        pcb.VibrationOff()

        f = open("IMU.txt", "w")
        f.write(str(list(map(binascii.b2a_hex, IMU_Data))))
        f.close()

       # imu = imu_analyzer("IMU.txt")

    # -----------------------------

    def testSNC():
        #   test SNC signals
        print("recording when all channels off")
        lp.startSNC()
        lp.stopSNC()

        print("recording when ch1 50hz sqr wave")
        pcb.setSNCCycle(1, 1000000 / 50)

        lp.startSNC()
        time.sleep(1)
        lp.stopSNC()

        print("recording when ch2 50hz sqr wave")
        pcb.setSNCCycle(1, 1000000 / 200)
        pcb.setSNCCycle(2, 1000000 / 50)

        lp.startSNC()
        time.sleep(1)
        lp.stopSNC()

        print("recording when ch3 50hz sqr wave")
        pcb.setSNCCycle(2, 1000000 / 200)
        pcb.setSNCCycle(3, 1000000 / 50)

        lp.startSNC()
        time.sleep(1)
        lp.stopSNC()

        print("turning sqr wave off")
        pcb.setSNCCycle(3, 1000000 / 200)

        lp.startSNC()
        time.sleep(1)
        lp.stopSNC()

        f = open("SNC.txt", "w")
        f.write(str(list(map(binascii.b2a_hex, SNC_Data))))
        f.close()

        snc = snc_analyzer("SNC.txt")

    # -----------------------------------

    # while True:
    #     lp.flash()
    #     cmd=input(">>>")
    #     try:
    #         lp.sendCmd(cmd)
    #     except Exception as e:
    #         print (e)

    #  lp.unpair()

    # init
    ser = serial.Serial("/dev/ttyACM0", 57600)
    pcb = pcbControl(ser)
    fc = FlashActions()
    lp = HandleBle()
    #initSNCinject()
    # lp.scan(9)
    #testIMU()
    # --------------------

    sn = board.serial_number
    pcb.selectBoard(nPcb)

    # Test VDIG
    Vdig = pcb.readVdig()
    board.vdig = [Vdig, True] if Vdig > 1.7 else [Vdig, False]

    # Test Burn
    board.burn = [True] if fc.flashDevice(sn) != -1 else [False]

    # Test RTT Inits
    fc.runDevice()
    fc.runDevice(board)
    # TODO - add log testing (Avigal's Parser)
    rtt_attributes = board.extractor.test()
    for _, attribute in enumerate(rtt_attributes):
        # TODO - adjust attributes
        # TODO - check for is damages better - in a different place?
        if attribute[0] == 'current':
            board.current = attribute
            if not attribute[-1]:
                board.is_damaged = True
        if attribute[0] == 'charger state':
            board.charger_state = attribute
            if not attribute[-1]:
                board.is_damaged = True
        if attribute[0] == 'battery voltage':
            board.battery_voltage = attribute
            if not attribute[-1]:
                board.is_damaged = True

    #board.current = rtt_attributes[0]
    #board.charger_state = rtt_attributes[1]
    #board.battery_voltage = rtt_attributes[2]


    # TODO - get mac address correctly
    mac_addr = 'D4:34:E0:2B:FB:C3'
    subprocess.run(['expect', './script.sh', mac_addr])
    lp.scan(sn)

    # TODO - adjust IMU and SNC testing
    testIMU()
    testSNC()

    return board
