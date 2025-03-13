from m16_driver import M16
from time import sleep

PORT = input("Please input the port where the modem is connected (e.g. COM3 or /dev/ttyUSB0): ")

CHANNEL = 1
POWER_LEVEL = 4
DIAGNOSTIC_MODE = False

# Initialize the modem
modem = M16(PORT, baudrate=9600, channel=CHANNEL, level=POWER_LEVEL, diagnostic=DIAGNOSTIC_MODE)

# If the report is to be saved enter a file name for it, else set it to None

report_file_name = None     # e.g. report.json
# Request and show the report
# If no valid packet is received check if the modem has power.
report = modem.request_report()
print(report)

# Send two bytes with the modem
two_bytes = 'Hi'
modem.send_two_bytes(two_bytes)
print(f"Sent {two_bytes} on channel {CHANNEL}")

# Give the modem time to send the two bytes before sending a new message
sleep(1)

# Send a longer message with the modem
msg = 'Hello from underwater'
modem.send_msg(msg)
print(f"Sent {msg} on channel {CHANNEL}")

# Close the modem
modem.close()