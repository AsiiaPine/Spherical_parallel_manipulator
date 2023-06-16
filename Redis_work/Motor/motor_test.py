import pandas as pd
from time import sleep
from libs import Gyems, CanBus

bus = CanBus()
motor = Gyems(bus)

# Create an empty DataFrame
df = pd.DataFrame(columns=['Speed', 'Forward or not'])

# Define pairs of values
pairs = [
    [360, -1],
    [120, 1],
    [180, -1]
]

# Iterate over the pairs and add them to the DataFrame
for pair in pairs:
    df.loc[len(df)] = pair

try:
    motor.enable()
    motor.set_zero()

    # Iterate through each row and retrieve values
    for index, row in df.iterrows():
        speed = row['Speed']
        forward = row['Forward or not']
        motor.set_angle(forward*360, int(speed))

        if forward == 0:
            print(f"Speed: {-speed}, Forward or not: {forward}")
        else:
            print(f"Speed: {speed}, Forward or not: {forward}")
        sleep(1)
    #motor.set_zero()
    print(df)

# Close the CAN bus connection
finally:
    motor.disable(True)
    bus.close()
