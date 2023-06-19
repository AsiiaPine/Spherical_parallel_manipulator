# Spherical_parallel_manipulator

## Reading the data from IMU:

These are the main ideas about work with serial port:

### Read from serial

To read a data from ESP, use serial port connection. Here is a **guide how to read data from serial port**
____
**Step 1:** Check if ESP is connected to your computer

```ls /dev/ttyUSB*```
___
**Step 2:** Check if there are some messages in the serial port

```sudo picocom /dev/ttyUSB0 -b 115200```

If you do not have the picocom package these are commands to install it:

- Ubuntu:
  ```sudo apt-get install picocom```

- Arch Linux:
  ```pacman -Sy picocom```

____
**Step 3:** Save the messages:

To save the output from the port, run the [Open_serial.py](Open_serial.py) -
code use [pyserial package](https://pypi.org/project/pyserial/) to open a connection.

Use the code as start point for any project, everything will work:)
___

### Messages 
The messages in a serial port are sent in the format you choose (or default for a board you are working with).

### Put your code intro a board

You can put your code into a board, it will run in inf loop.

How to do this?

____
**Step 1:** Connect to the board shell:



```rshell -p /dev/ttyUSB0 -b 115200```

- If the process is stopped during the step "Trying to connect to REPL ...", try to push the reset button on a board, or try
  the command with sudo. If it doesn't help try to reinstall the rshell.

___
**Step 2:** Upload a script(s) with rshell

- If you need to upload only the main.py file

```cp path/to/main.py /pyboard/main.py```

- If you need to upload many files

```cp -r path/to/*.py /pyboard/```

- If you need to upload many files with a folder

````
mkdir /pyboard/<folder_name>
cp -r path/to/<folder_name>/*.py /pyboard/<folder_name>/
````
___
**Step 4:** Close the rshell

Press ``ctrl+C``

### Start your code work in the board

- The guide **for python scripts**

Run your code
___
**Step 1:** Install picocom

```sudo apt-get install picocom```
___
Step 2: Open shell

```sudo picocom /dev/ttyUSB0 -b 115200```
___
Step 3: Run script

Run script: ```ctrl+d```

Stop script: ```ctrl+c```

Exit from shell: ```ctrl+a + ctrl+q```


_____
# IMU calibration

To save the values of IMU with the time corresponding to each value that is read from IMU, run IMU_serial_reading_for_calibration.py
