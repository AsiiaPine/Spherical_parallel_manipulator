from time import sleep, perf_counter

from libs import Gyems, CanBus

bus = CanBus()
motor = Gyems(bus)

try:
    motor.enable()
    motor.set_zero()
    motor.set_angle(360, 120)
    sleep(10)

    while True:
        print(motor.info())
        sleep(0.1)
except KeyboardInterrupt:
    pass

finally:
    motor.disable(True)
    bus.close()

# from time import sleep, perf_counter
# from libs import Gyems, CanBus

# bus = CanBus()
# motor = Gyems(bus)

# try:
#     motor.enable()
#     motor.set_zero()
#     motor.set_angle(360, 16)
#     sleep(10)

#     # Variables to store previous position and time
#     prev_position = motor.info().position
#     prev_time = perf_counter()

#     while True:
#         # Get current position and time
#         current_position = motor.info().position
#         current_time = perf_counter()

#         # Calculate change in position and time
#         delta_position = current_position - prev_position
#         delta_time = current_time - prev_time

#         # Calculate velocity
#         velocity = delta_position / delta_time

#         # Print velocity
#         print("Velocity:", velocity)

#         # Update previous position and time
#         prev_position = current_position
#         prev_time = current_time

#         sleep(0.1)

# except KeyboardInterrupt:
#     pass

# finally:
#     motor.disable(True)
#     bus.close()