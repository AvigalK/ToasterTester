import subprocess
import time
import argparse
import sys

from bluepy import btle

class BLE:
    from bluepy import btle
    def __init__(self):
        from bluepy import btle
        
        
class ScanPrint(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)
        

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            status = "new"
        elif isNewData:
            status = "update"
        else:
            status = "old"

        print ('    Device (%s): %s (%s), %d dBm %s' %
               (status,
                   dev.addr,
                   dev.addrType,
                   dev.rssi,
                   ('' if dev.connectable else '(not connectable)'))
               )
        for (sdid, desc, val) in dev.getScanData():
            if sdid in [8, 9]:
                print ('\t' + desc + ': \''  + val+ '\'')
            else:
                print ('\t' + desc + ': <' + val + '>')
        if not dev.scanData:
            print ('\t(no data)')
        print
def main():
    
    try:
        scanner = btle.Scanner().withDelegate(ScanPrint())
        print ("Scanning for devices...")
        devices = scanner.scan(10.0) 


    
if __name__ == "__main__":
    main()
