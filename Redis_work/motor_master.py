import json
import pandas as pd
from time import sleep
from Motor.libs import Gyems, CanBus

bus = CanBus()
motor = Gyems(bus)


def load_data_from_json(key_str: int|str):
    try:
        with open('motor_speeds.json') as f:
            motor_tests = json.loads(json.load(f))
        for key, val in motor_tests.items():
            if str(key_str) in key:
                motor_tests = val
                return motor_tests
            raise ValueError(f'tests_data do not have such word in keys {key_str}')
        return {}
    except ValueError:
        print(f'tests_data do not have such word in keys {key_str}')
        return {}


tests_data = load_data_from_json(1)

try:
    for params in tests_data:
        motor.enable()
        motor.set_zero()
        angle = params["angle"]

        # Iterate through each row and retrieve values
        speed = params['speed']
        forward = params['forward']
        motor.set_angle(forward*angle, int(speed))

        if forward == 0:
            print(f"Speed: {-speed}, Forward or not: {forward}")
        else:
            print(f"Speed: {speed}, Forward or not: {forward}")
        sleep(1)


# Close the CAN bus connection
finally:
    pass
    motor.disable(True)
    bus.close()


# # Create an empty DataFrame
# df = pd.DataFrame(columns=['Speed', 'Forward or not'])

# # Define pairs of values
# pairs = [
#     [360, -1],
#     [120, 1],
#     [180, -1]
# ]

# # Iterate over the pairs and add them to the DataFrame
# for pair in pairs:
#     df.loc[len(df)] = pair

# try:
#     motor.enable()
#     motor.set_zero()

#     # Iterate through each row and retrieve values
#     for index, row in df.iterrows():
#         speed = row['Speed']
#         forward = row['Forward or not']
#         motor.set_angle(forward*360, int(speed))

#         if forward == 0:
#             print(f"Speed: {-speed}, Forward or not: {forward}")
#         else:
#             print(f"Speed: {speed}, Forward or not: {forward}")
#         sleep(1)
#     #motor.set_zero()
#     print(df)

# Close the CAN bus connection
# finally:
#     motor.disable(True)
#     bus.close()