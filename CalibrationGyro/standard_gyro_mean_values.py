# standard values read from mobile phone's gyroscope. Y-axis
# (Mean value: -0.004503333333333333)

import csv
import datetime

start_time = datetime.datetime.strptime('17:40:50:000', '%H:%M:%S:%f')
end_time = datetime.datetime.strptime('17:40:52:000', '%H:%M:%S:%f')

data = []

# Read the CSV file
with open('gyroscope_y.csv', 'r') as file:
    reader = csv.reader(file, delimiter=',')
    next(reader)  # Skip the header row
    for row in reader:
        timestamp = datetime.datetime.strptime(row[0].replace(',', ''), '%H:%M:%S:%f')
        if start_time <= timestamp <= end_time:
            print(timestamp, float(row[2])) # Y-axis. To change an axis, change index row[]
            data.append(float(row[1]))  # Assuming column index starts from 0

# Calculate the mean if there is at least one data point
if len(data) > 0:
    mean_value = sum(data) / len(data)
    print("Mean value:", mean_value)
else:
    print("No data points within the specified time range.")