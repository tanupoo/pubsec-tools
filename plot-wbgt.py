#!/usr/bin/env python

import sys
import json
import matplotlib.pyplot as plt

result = json.load(sys.stdin)

x = result["hour"]
y = result["wbgt"]

fig = plt.figure(figsize=(8, 4))
ax1 = fig.add_subplot(1,1,1)
ax1.set_xlabel("hour")
ax1.set_ylabel("wbgt")
ax1.set_xticks(list(range(0,24,1)))
ax1.set_yticks(list(range(15,41,5)))
ax1.set_yticks(list(range(15,41,1)), minor=True)
ax1.set_xlim(1,24)
ax1.set_ylim(15,40)
ax1.grid(b=True, axis="x", which="major")
ax1.grid(b=True, axis="y", which="major")
ax1.grid(b=True, axis="y", which="minor")
ax1.plot(x,y)
plt.tight_layout()
plt.show()

