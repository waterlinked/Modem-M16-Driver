# Instructions for developers

## Pytest
The two tests located in [test_files](test_files/) are written as pytests, to run them make sure that `pytest` is 
installed *(latest tested version is pytest==8.3.5)* and that the **modems are connected** to the PC 
and a PSU giving *3V*.

The tests can be run using the following command from the root directory:

```bash
pytest
```

### Test contents:

`single_driver_test.py`\
Tests the modem's functionality related to states (channel, power level, etc.).\
The modem is tested by changing a value and verifying it in the report.


`dual_driver_test.py`\
Tests communication between the modems, requiring both to be connected.\
The test sends known values and verifies what is received.


## Building .exe
The .exe file is built with the python package `pyinstaller` on Windows *(latest tested version is pyinstaller==6.12.0)*

To build the .exe run the following command:

```Powershell
pyinstaller --onefile gui.py
```

The .exe file will be placed in a new folder `dist`, another folder `build` and a file `gui.spec` will also be created.\
gui.exe can be moved and both folders and the .spec file can be removed.

Alternatively run the command:

```Powershell
pyinstaller --onefile gui.py
while (-not (Test-Path "dist/gui.exe")) { Start-Sleep -Seconds 1 }
mv dist/gui.exe gui.exe -Force
Remove-Item -Recurse -Force build, dist, gui.spec
```