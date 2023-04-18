import serial
import numpy as np

# Opening serial connection with device named by your system as ttyUSB0. Use baudrate, specified by the device!
serialPort = serial.Serial(port='/dev/ttyUSB0', baudrate=115200)
print(serialPort.name)  # check which port was really used

# list with future fetched messages from the port
input_array = []
try:
    while (1):

        # Wait until there is data waiting in the serial buffer
        if (serialPort.in_waiting > 0):
            # Read data out of the buffer until a carraige return / new line is found
            serialString = serialPort.readline()

            # Print the contents of the serial data
            print(serialString.decode('Ascii'))
            # Collecting the data into input_array and the data decoding from binary to readable Ascii.
            # Split sep parameter might be specified if the message has non-default delimiter )
            input_array.append(list(map(int, serialString.decode('Ascii').split())))
except:
    serialPort.close()  # close port
    a = np.asarray(input_array)  # convering the input array to numpy (to readable storing in the )
    np.savetxt("serial_port_data.csv", a, delimiter=";")  # saving the result into csv file
    print("To read the data, open serial_port_data.csv file!")
