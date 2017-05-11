#!/usr/bin/python3

import datetime
import matplotlib.pyplot as plt

weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

def plot(temp, humidity):

    x = [1, 2, 3, 4, 5]
    plt.subplot(211)


    plt.plot(x, temp, 'r-', label='Temperature in C')
    plt.axis([0, 6, 0, 35])
    plt.xticks(x, [])

    plt.xlabel('')

    plt.ylabel('Temperature in C')

    plt.subplot(212)
    plt.axis([0, 6, 0, 100])
    plt.xticks(x, ['Today',
                   'Tomorrow',
                   weekdays[(datetime.date.today().weekday() + 2) % 6],
                   weekdays[(datetime.date.today().weekday() + 3) % 6],
                   weekdays[(datetime.date.today().weekday() + 4) % 6]])

    plt.plot(x, humidity, 'b-', label='Humidity in %')
    plt.xlabel('Weekdays')
    plt.ylabel('Humidity in %')

    plt.savefig('plot.png')
