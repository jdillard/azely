"""Dayplot of solar objects' elevations with given date, location, and timezone."""

import azely
import numpy as np
import matplotlib.pyplot as plt

# date and locations
date = '2018-01-01'
location = 'alma observatory'
timezone = 'local sidereal time'

# calculation
c = azely.Calculator(location, timezone, date)
hr = np.linspace(0, 24, 601) # [0, 24] hr
azels = c('solar', hr) # OrderedDict

# plotting
for name, azel in azels.items():
    plt.plot(hr, azel.el, label=name)

plt.xlim(0, 24)
plt.ylim(0, 90)
plt.title(f'{c.location["name"]} / {c.date}')
plt.xlabel(f'{c.timezone["name"]} (hr)')
plt.ylabel('Elevation (deg)')
plt.legend()
plt.show()
