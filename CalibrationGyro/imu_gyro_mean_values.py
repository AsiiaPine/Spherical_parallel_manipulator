# read values from imu's gyroscope 

# Y: Mean value: -32512.0
# X: Mean value: -3870.3574660633485
# Z: Mean value: 2390.255605381166
import csv
import datetime

# for y
# start_time = datetime.datetime.strptime('17:40:51:000', '%H:%M:%S:%f')
# end_time = datetime.datetime.strptime('17:40:53:000', '%H:%M:%S:%f')

# start_time = datetime.datetime.strptime('17:40:52:026', '%H:%M:%S:%f')
# end_time = datetime.datetime.strptime('17:40:53:830', '%H:%M:%S:%f')


# for x
# start_time = datetime.datetime.strptime('17:38:00:211', '%H:%M:%S:%f')
# end_time = datetime.datetime.strptime('17:38:02:132', '%H:%M:%S:%f')

# for z
start_time = datetime.datetime.strptime('17:35:30:286', '%H:%M:%S:%f')
end_time = datetime.datetime.strptime('17:35:32:197', '%H:%M:%S:%f')

data = []

# Read the CSV file9

with open('imu_results_z.csv', 'r') as file:
    reader = csv.reader(file, delimiter=';')
    next(reader)  # Skip the header row
    for row in reader:
        timestamp = datetime.datetime.strptime(row[0], '%H:%M:%S:%f')
        if start_time <= timestamp <= end_time:
            print(timestamp, ' ', int(row[9]))
            # Y-axis. To change an axis, change index row[]
            data.append(int(row[9]))  # Assuming column index starts from 0

# Calculate the mean if there is at least one data point
if len(data) > 0:
    mean_value = sum(data) / len(data)
    print("Mean value:", mean_value)
else:
    print("No data points within the specified time range.")
