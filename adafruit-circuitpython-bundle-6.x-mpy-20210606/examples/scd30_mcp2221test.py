# SPDX-FileCopyrightText: 2021 by Carter Nelson, written for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense
import time
import board
import adafruit_scd30

i2c = board.I2C()  # uses board.SCL and board.SDA
scd = adafruit_scd30.SCD30(i2c)

# The SCD30 reset generates a hiccup on the SCL and SDA lines
# which can end up not being handled well by different hosts.
scd.reset()

# The MCP2221 is known to not like the SCD30 reset hiccup.
# See below for more information:
# https://github.com/adafruit/Adafruit_CircuitPython_SCD30/issues/2
# Can get around it by resetting via this hack.
# pylint:disable=protected-access
if hasattr(i2c, "_i2c"):
    # we're using Blinka, check for MCP2221
    if hasattr(i2c._i2c, "_mcp2221"):
        # reset it
        i2c._i2c._mcp2221._reset()

while True:
    # since the measurement interval is long (2+ seconds) we check for new data before reading
    # the values, to ensure current readings.
    if scd.data_available:
        print("Data Available!")
        print("CO2:", scd.CO2, "PPM")
        print("Temperature:", scd.temperature, "degrees C")
        print("Humidity:", scd.relative_humidity, "%%rH")
        print("")
        print("Waiting for new data...")
        print("")

    time.sleep(0.5)
