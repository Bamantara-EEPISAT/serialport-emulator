# Mock Serial Port Project

This project simulates the behavior of a serial communication system for testing purposes. You can use it to transmit or receive data over a virtual serial port. It provides functionality to interact with COM ports, making it suitable for testing serial communication without needing physical hardware.

## Prerequisites

Before running the project, make sure you have set up virtual serial ports. You can either use **com0com** or **Free Virtual Serial Port Tools** to create virtual serial port pairs. The software required for this setup can be found in the `3rd_party_software` folder.

### 1. com0com

[com0com](https://sourceforge.net/projects/com0com/) is a free and open-source tool for creating virtual COM ports. It allows the creation of virtual COM port pairs that can be used to test serial communication.

1. Download and install com0com from the [official website](https://sourceforge.net/projects/com0com/).
2. After installation, use the `setupc.exe` tool to create a pair of virtual COM ports, e.g., COM1 and COM2. These ports will be used for the communication between your program and the mock serial port.

### 2. Free Virtual Serial Port Tools

[Free Virtual Serial Port Tools](https://www.hw-group.com/software/free-virtual-serial-port) is another software that can be used to create virtual COM ports and simulate serial communication.

#### Steps for Setup:

1. Download and install **Free Virtual Serial Port Tools** from the [official website](https://www.hw-group.com/software/free-virtual-serial-port).
2. Once installed, open **Virtual Serial Port Driver** and create two virtual COM ports. These ports will act as the mock serial ports.
3. **Important**: If you're using **Free Virtual Serial Port Tools**, make sure to use the **Local Bridges Mode**:
   - In the software interface, you can create two ports (e.g., COM3 and COM4) and bridge them together.
   - Set up a local bridge to ensure that data sent from one port is received by the other, simulating the serial communication.

---

### 3. Using Mock Serial Port Binary

You can use the precompiled `mock_serialport.exe` binary to easily simulate the serial port communication. The executable provides two main modes: **transmit** and **receive**. Follow these instructions to use it.

#### Display Help

To display the available options and usage guide for `mock_serialport.exe`, run the following command:

```bash
mock_serialport.exe --help
```

This will show you all the available command-line arguments for both **transmit** and **receive** modes.

#### Transmit Mode

To run the application in **transmit mode**, you need to specify the following parameters:

- `--com-port` : The COM port to use (e.g., COM1)
- `--baud-rate` : The baud rate for the serial communication (e.g., 9600)
- `--mode transmit` : Specify transmit mode
- `--file-path` : Path to the CSV file containing telemetry data (e.g., `telemetry_data.csv`)
- `--loop-mode` (optional) : If enabled, the transmission will repeat indefinitely.
- `--delimiter` (optional) : Specify a custom delimiter, such as a comma `,`, or newline `\n`.

For example, to transmit telemetry data with a custom delimiter and enable loop mode:

```bash
mock_serialport.exe --com-port COM1 --baud-rate 9600 --mode transmit --file-path telemetry_data.csv --loop-mode --delimiter ","
```

This command will send the contents of the `telemetry_data.csv` file over the specified COM port. The `--loop-mode` flag will ensure the data transmission continues indefinitely.

#### Receive Mode

To run the application in **receive mode**, specify the following parameters:

- `--com-port` : The COM port to use (e.g., COM1)
- `--baud-rate` : The baud rate for the serial communication (e.g., 9600)
- `--mode receive` : Specify receive mode

For example, to receive data from the specified COM port:

```bash
mock_serialport.exe --com-port COM2 --baud-rate 9600 --mode receive
```

This command will continuously listen for incoming data on the specified COM port and display it on the console.

---

With the `mock_serialport.exe` binary, you no longer need to run the Rust project directly. You can easily simulate serial communication by running the appropriate command for transmit or receive modes.

### 3. Installing Dependencies (Optional)

Ensure that you have all dependencies installed for the project to work correctly:

1. **Rust**: Ensure that the Rust programming language is installed. You can install it by following the instructions on the [official website](https://www.rust-lang.org/).
2. **serialport crate**: The project depends on the `serialport` crate to communicate with virtual COM ports. The `Cargo.toml` file includes this dependency, and it will be automatically installed when you build the project.

To install the required dependencies, run:

```bash
cargo build
```

This will download and install the necessary dependencies.

### 4. Generating Telemetry Data

Before transmitting or receiving data, you need to generate a CSV file containing telemetry data for emulation.

1. In the parent directory, look for the `telemetry_generator` python script.
2. Run the Python script `telemetry_generator.py` to generate the `telemetry_data.csv` file, which contains mock telemetry data.

#### To generate the telemetry data, run:

```bash
python telemetry_generator.py
```

This will create a `telemetry_data.csv` file in the same directory. This file will be used by the Rust application to transmit data over the virtual serial port.

### 5. Running the Project

Once the virtual serial ports are set up and the telemetry data CSV file is generated, you can run the project in **transmit** or **receive** mode.

#### Transmit Mode

To transmit data, specify the mode as `transmit`, the COM port, and the path to the generated CSV file containing telemetry data:

```bash
cargo run -- --com-port COM1 --baud-rate 9600 --mode transmit --file-path telemetry_data.csv --loop-mode --delimiter ","
```

This command will continuously send the contents of the `telemetry_data.csv` file with a specified delimiter. The `--loop-mode` flag ensures that the transmission repeats indefinitely.

#### Receive Mode

To receive data from the COM port, use the `receive` mode:

```bash
cargo run -- --com-port COM2 --baud-rate 9600 --mode receive
```

This command will continuously receive and print data from the specified COM port.

## Troubleshooting

- **COM Port Issues**: If you have trouble with the COM ports not appearing or not functioning, ensure that the virtual serial ports were created successfully using either `com0com` or `Free Virtual Serial Port Tools`.
- **Permissions**: Make sure that your user account has the necessary permissions to access the COM ports, especially on Windows where administrator privileges might be required to create virtual ports.

## Conclusion

This project allows you to simulate serial communication by using virtual COM ports for testing purposes. Whether you use **com0com** or **Free Virtual Serial Port Tools**, you can easily set up a testing environment that mimics real-world serial communication.

---

#### Folder Structure:
```
/3rd_party_software
    /setup_com0com
    /com0com_driver
    /FreeVirtualSerialPortTools
/mock_serialport.exe
/telemetry_generator.py
/telemetry_data.csv
/src
    (project files)
README.md
```

### License

The source code for this project is licensed under the **MIT License**.

```text
MIT License

Copyright (c) 2024 Muhammad Tsaqif Mukhayyar (Bamantara EEPISAT)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```