# This pytest needs to run with hardware connected

import pytest
from m16_driver import M16

MODEM_PORT_1 = "COM3"
MODEM_PORT_2 = "COM4"

@pytest.fixture
def modem1():
    """Create an M16 instance for real hardware testing."""
    return M16(port=MODEM_PORT_1, baudrate=9600, timeout=0.5, diagnostic=False, channel=1, level=4)

@pytest.fixture
def modem2():
    """Create an M16 instance for real hardware testing."""
    return M16(port=MODEM_PORT_2, baudrate=9600, timeout=0.5, diagnostic=False, channel=1, level=4)

def test_send_two_bytes(modem1, modem2):
    modem1.send_two_bytes("Hi")
    packet = modem2.read_packet().decode('ISO-8859-1')
    assert packet == "Hi", f"the recieved data from modem1 is not 'Hi'"
    
    modem2.send_two_bytes("Hi")
    packet = modem1.read_packet().decode('ISO-8859-1')
    assert packet == "Hi", f"the recieved data from modem1 is not 'Hi'"

def test_send_msg(modem1, modem2):
    message = ""
    modem1.send_msg("This is a longer message")
    packet = modem2.read_packet().decode('ISO-8859-1')
    message += packet
    assert message == "This is a longer message", f"the longer message from modem 1 does not match {message}"

    message = ""
    modem2.send_msg("This is a longer message")
    packet = modem1.read_packet().decode('ISO-8859-1')
    message += packet
    assert message == "This is a longer message", f"the longer message from modem 2 does not match {message}"