# Spherical_parallel_manipulator

## Reading the data from IMU:

There are main ideas about work with IMU:

### 1- How to read from serial

To read a data from the ESP, use serial port connection. Here is **guide how to read data from serial port**
____
**Step 1:** Check is ESP connected to your computer

```ls /dev/ttyUSB*```
___
**Step 2:** Check if there is some messages in the serial port

```sudo picocom /dev/ttyUSB0 -b 115200```

If you do not have the picocom package there are commands to install it:

- Ubuntu:
  ```sudo apt-get install picocom```

- Arch Linux:
  ```pacman -Sy picocom```

____
**Step 3:** Save the messages:

To save the output from the port, run the [Open_serial.py](Open_serial.py) -
code use [pyserial package](https://pypi.org/project/pyserial/) to open a connection.

Use the code as start point for any project all will work:)
___

### 2 - The messages in a serial port sends in the format you choose (or default for a board you are working with).

### 3 - You can put into a board your code which will run in inf loop

How to do this?

____
**Step 1:** Connect to shell inside the board:



```rshell -p /dev/ttyUSB0 -b 115200```

- If the process stopped into the step Trying to connect to REPL ..., try to push the button reset on a board, or try
  the command with sudo. If it doesn't help try to reinstall the rshell.

___
**Step 2:** Upload a script(s) with rshell

- If you need upload only file main.py

```cp path/to/main.py /pyboard/main.py```

- If you need to upload many files

```cp -r path/to/*.py /pyboard/```

- If you need to upload many files with folder

````
mkdir /pyboard/<folder_name>
cp -r path/to/<folder_name>/*.py /pyboard/<folder_name>/
````
___
**Step 4:** Close the rshell

Press ``ctrl+C``

### 4 - Start your code work in the board

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