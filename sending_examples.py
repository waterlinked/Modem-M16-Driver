from m16_driver import M16
from time import sleep

PORT = "COM3"   # This may vary on operating system and where the modem is connected
CHANNEL = 1
POWER_LEVEL = 4
DIAGNOSTIC_MODE = False

# Initialize the modem
modem = M16(PORT, baudrate=9600, channel=CHANNEL, level=POWER_LEVEL, diagnostic=DIAGNOSTIC_MODE)

# If the report is to be saved enter a file name for it, else set it to None

reporr_file_name = None     # e.g. report.json
# Request and show the report
report = modem.request_report()
print(report)

# Send two bytes with the modem
two_buytes = 'Hi'
modem.send_two_bytes(two_buytes)
print(f"Sendt {two_buytes} on channel {CHANNEL}")

# Give the modem time to send the two bytes before sending a new message
sleep(1)

# Send a longer message with the modem
msg = 'Hello from underwater'
modem.send_msg(msg)
print(f"Sendt {msg} on channel {CHANNEL}")

# Close the modem
modem.close()