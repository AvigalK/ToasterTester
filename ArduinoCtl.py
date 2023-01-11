
if __name__ == '__main__':
    import  sys
    import serial
    ser = serial.Serial ("/dev/ttyACM0", 57600)
    string = "snc1 power on\n"

    ser.write(bytes(string, 'ascii'))
    while True:
        print (".")
    #    print (ser.read())

    
    
    sys.exit(main(sys.argv))
