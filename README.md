# Water Linked Python Modem-M16-Driver

## About
This repository includes a simple app to interact with the modem, a driver for easy communication with the modem,
an example report and two example scripts for sending and receiving messages through the modems. For more detailed
information about the M16 modem and its interface, please visit the 
[official documentation](https://docs.waterlinked.com/modem-m16/modem-m16/).

---
**NOTE:**

- For consistency place both modems in the same bucket with water.

- When reading a report the power level 4 will be shown as 0, the conversion is 4 - *PW* where *PW* is the power level
from the report. For more information please visit the 
[official packet structure documentation](https://docs.waterlinked.com/modem-m16/modem-m16-uart-interface/#packet-structure-of-the-diagnostic-report).



### App.exe
This executable facilitates easy verification of the working of the modem, it also highlights some features of the modem
and is a good starting point to get to know the functionality of the modem without Python. The app is a tkinter app 
that communicates with the modem through `m16_driver.py`.

The default port is set to ``COM3``, the user may need to change this to the appropriate port.

### m16_driver.py
A driver for simple interaction with the modem, it includes functionality for changing of modes, channels and levels.
It also includes functionality for sending 2 bytes and longer messages as well as requesting and saving reports.


### sending_examples.py
Simple script for requesting a report and sending a 2 bytes long message.

### receive_example.py
example script for continuously listening to the modem.

### report.json
This is an example file that shows what a report decoded with the `M16.decode_packet()`from the modem looks like, 
saved to a .json file

## Requirements
- [Python3](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/installation/)
- [venv](/https://docs.python.org/3/library/venv.html)
- [requirements.txt](requirements.txt)

## Installation
The driver and app has been developed with python3.10. In order to run the scripts Python must be installed, this can 
either be done with the link in the Requirements section or from the windows store. venv is standard in Pyhton3.10 on 
Windows but on linux the user may have to install it, that can be done with the command:

```
sudo apt update
sudo apt install python3 python3-venv
```


To be able to run the code this repository has to be cloned that can either be done through the terminal , GitHub CLI or 
by downloading the ZIP file and extracting it to your desired location. The next step is to navigate to the repository 
on your machine, this can be done with the command below:

```
git clone https://github.com/waterlinked/Modem-M16-Driver.git
cd Modem-M16-Driver
```

Next we need to create a virtual environment, the easiest way is from the terminal. On Windows this can be done by 
pressing the ``Windows key`` and searching for ``terminal``. On linux it can be done by pressing ``ctrl + alt + t``. 
In the terminal run the command:

```
python3 -m venv venv
```

Next we need to activate the environment, in powershell on Windows the command is:
```
.\venv\Scripts\Activate.ps1   
```
On linux use this command:
```bash
source venv/Scripts/activate
```

Finally, when the virtual environment is activated install the dependencies with the command:\
(It is activated when <span style="color:lightgreen"> (venv)</span> appears before the terminal path)
```
pip install -r requirements.txt
```

After this the python scripts can be run with the command `python <example_script.py>`

### GUI app for Linux
If you want to use the gui.py app on linux, ``tkinter`` has to be downloaded, this can be done with the command:

```bash
sudo apt install python3-tk
```

## Screenshot

Screenshot of the app before connecting to the modem\
<img src="media/app_unconnected.png" alt="App before connection to modem" width="500">\
Screenshot of the app after connecting to the modem and requesting a report.\
<img src="media/app_connected_transparent.png" alt="App in transparent mode" width="500">\
Screenshot of the app while connected and in diagnostic mode\
<img src="media/app_connected_diagnostic.png" alt="App in diagnostic mode" width="1000">