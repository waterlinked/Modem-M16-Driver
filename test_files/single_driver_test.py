# This pytest needs to run with hardware connected

import os
import json
import pytest
from m16_driver import M16

MODEM_PORT = "COM3"

def assert_report_value(report, key):
    """Helper function to check if a key exists in the report."""
    assert report is not None, "request_report() returned None"
    assert key in report, f"{key} key missing in report: {report}"
    print(report)

def convert_level_from_report(level: int) -> int:
    """Helper function to convert the power level value from the report back to domain we are sending in"""
    return 4 - level

@pytest.fixture
def modem():
    """Create an M16 instance for real hardware testing."""
    return M16(port=MODEM_PORT, baudrate=9600, timeout=0.5, diagnostic=False)

def test_initialize_modem(modem):
    """Test if modem initializes without errors."""
    assert modem.ser.is_open, f"Serial port is not open..."

def test_set_channel(modem):
    """Test if the modem channel can be set and verified correctly."""
    key = 'CHANNEL'
    # Test valid entries
    for i in [5, 8, 12]:
        success = modem.set_channel(i)
        assert success, f"Failed to set channel to {i}"

        report = modem.request_report()
        assert_report_value(report, key)
        assert report[key] == i, f"Expected channel {i}, but got {report[key]} from report"
    
    # Test invalid entries
    # Denne feiler på om i = True fordi True == 1 -> True
    for i in [200, "e", -2]:
        fail = modem.set_channel(i)
        assert not fail, f"Channel should be invalid"

        report = modem.request_report()
        assert_report_value(report, key)
        assert report[key] != i, f"Expected channel {i}, and got {report[key]} from report"

def test_set_level(modem):
    """Test if the modem power level can be set and verified correctly"""
    key = 'LEVEL'
    # Test valid entries
    for i in [1, 2, 3, 4]:
        success = modem.set_level(i)
        assert success, f"Failed to set power level {i}"

        report = modem.request_report()
        assert_report_value(report, key)
        assert convert_level_from_report(report[key]) == i, f"Expected power level {i}, \
            but got {report[key]} from report"

    # Test invalid entries
    for i in [-1, "e", 100]:
        fail = modem.set_level(i)
        assert not fail, f"Power level should be invalid"
        
        report = modem.request_report()
        assert_report_value(report, key)
        assert convert_level_from_report(report[key]) != i, f"Expected power level {i}, \
            and got {report[key]} from report"


def test_set_diagnostic_mode(modem):
    modem.set_diagnostic_mode()
    report = modem.request_report()
    assert_report_value(report, 'DIAGNOSTIC_MODE')
    assert report['DIAGNOSTIC_MODE'] == True

# FAILING 
# def test_reset_diagnostic_mode(modem):
#     modem.reset_diagnostic_mode()
#     report = modem.read_packet()
#     sleep(5)
#     report = modem.read_packet()
#     report = modem.decode_packet(report)
#     assert_report_value(report, 'DIAGNOSTIC_MODE')
#     assert report['DIAGNOSTIC_MODE'] == False

def test_toggle_mode(modem):
    report = modem.request_report()
    previous_mode = report['DIAGNOSTIC_MODE']
    modem.toggle_mode()
    report = modem.request_report()
    current_mode = report['DIAGNOSTIC_MODE']
    assert current_mode is not previous_mode, f"Mode is the same before and after mode toggle"

def test_update_state_from_report(modem):
    new_channel = 4
    new_level = 1
    new_diagnostic = False

    modem.set_channel(new_channel)
    modem.set_level(new_level)
    modem.reset_diagnostic_mode()

    assert modem.channel == 4, f"Internal state for channel is {modem.channel} and not {new_channel}"
    assert modem.level == 1, f"Internal state for level is {modem.level} and not {new_level}"
    assert modem.diagnostic == False, f"Intenal state for diagnostic mode is {modem.diagnostic} \
        and not {new_diagnostic}"
    
def test_save_report_to_file(modem):
    file_name = "pytest_report.json"

    # Request a report and have it saved to a file.
    report = modem.request_report(file_name)
    assert report is not None, "request_report() did not return a valid report."
    
    # Ensure the file exists
    assert os.path.exists(file_name), f"Report file {file_name} was not created."
    
    # Open the JSON file and verify required keys exist.
    with open(file_name, "r") as f:
        saved_report = json.load(f)
    
    # Check that some expected fields are in the saved report.
    for key in ["CHANNEL", "LEVEL", "DIAGNOSTIC_MODE"]:
        assert key in saved_report, f"Key '{key}' missing in saved report."
    
    # Delete the file after verification.
    os.remove(file_name)