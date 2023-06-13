import asyncio
import redis
import serial
import numpy as np
import pandas as pd
import json
from redis import asyncio as aioredis
from message_broker import RedisMessageBroker
from config import headers


redis = aioredis.from_url("redis://localhost:6379/0")
broker = RedisMessageBroker(redis)

serialPort: serial.Serial

def open_serial_port():
    global serialPort
    serialPort = serial.Serial(port='/dev/ttyUSB0', baudrate=115200)  # open serial port
    print(serialPort.name)  # check which port was really used


async def read_serial_and_post_to_redis():
    """
    Read data from IMU using serial port and post to redis stream.
    """

    open_serial_port()
    while (1):
        try:
            # Wait until there is data waiting in the serial buffer
            if (serialPort.in_waiting > 0):

                # Read data out of the buffer until a carraige return / new line is found
                serialString = serialPort.readline()

                # Get the contents of the serial data
                data = list(map(int, serialString.decode('Ascii').split(" ")))

                # Build a dict with received data.
                result = {}
                for val, header in zip(data, headers):
                    result[header] = val
                    print(header, val)

                await broker.publish("imu_data", json.dumps(result))


        except KeyboardInterrupt:
            serialPort.close() 
            await redis.delete('imu_data')
            return
        except:
            print("Strange exeption")
            serialPort.close() 
            open_serial_port()


if __name__ == "__main__":
    asyncio.run(read_serial_and_post_to_redis())