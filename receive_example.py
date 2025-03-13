from m16_driver import M16

PORT = input("Please input the port where the modem i connected: ")

CHANNEL = 1
POWER_LEVEL = 4
DIAGNOSTIC_MODE = False

# Initialize the modem
modem = M16(PORT, baudrate=9600, channel=CHANNEL, level=POWER_LEVEL, diagnostic=DIAGNOSTIC_MODE)

print(f"Starting loop, \nexit with ctrl + c")
while True:
    packet = modem.read_packet()
    if packet is not None:    
        print(f"Recieved: {str(packet)}")
