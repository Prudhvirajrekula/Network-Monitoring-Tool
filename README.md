# Basic Network Monitoring

A comprehensive network monitoring and security tool that detects open ports and their associated processes. It provides a feature-rich GUI for real-time monitoring, visualization, and management of network activities.

## Features

- **Network Monitoring:** Real-time monitoring of open ports and associated processes
- **Port Management:** Enable/disable ports with detailed process information
- **IP Information:** Display both local and public IP information with geolocation details
- **Network Scanning:** Scan and identify devices connected to your local network
- **Trace Visualization:** Trace network routes with interactive geographic visualization
- **Data Analysis:** Multiple data visualization options for network traffic analysis
- **Reporting:** Generate comprehensive reports on network activities and security
- **Theme Options:** Support for both light and dark mode UI

## Requirements

- Python 3.11+
- PyQt5
- psutil
- Additional packages (see requirements.txt)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/jash218/Basic-Network-Monitoring.git
   cd Basic-Network-Monitoring
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Network Task Manager

To run the Network Task Manager, execute the `main.py` file:

```bash
python main.py
```

This will launch the GUI for monitoring open ports and their associated processes.

## System Architecture

The application is built with a modular architecture:

- **Core Module:** Contains backend functionality for network operations
  - `backend.py`: Network monitoring and port management
  - `dataanalysis.py`: Data processing and analysis algorithms
  - `reports.py`: Report generation functionality

- **UI Module:** Contains frontend components
  - `frontend.py`: Main application window and UI management
  - `networkscanner.py`: Network scanning interface
  - `tracevisualizer.py`: Route tracing and visualization
  - `portblocker.py`: Port blocking interface
  - Additional UI components for settings, information, etc.

## Key Capabilities

### Network Traffic Monitoring
Monitor bandwidth usage, active connections, and protocol distribution in real-time. The application logs network activities for historical analysis.

### Port Management
View all open ports with their associated processes, PID, and CPU usage. Enable or disable ports as needed for security purposes.

### Network Scanning
Scan your local network to discover connected devices, showing IP addresses, MAC addresses, and device information.

### Trace Visualization
Perform visual traceroutes to see the path your traffic takes to reach destinations. Results are displayed on an interactive map showing the geographic location of each hop.

### Data Analysis
Multiple visualization options are available:
- Bandwidth usage over time
- Protocol distribution
- Top talkers (most active IPs)
- Packet loss
- Connection latency

### Reporting
Generate various reports including:
- Daily traffic summaries
- Top bandwidth consumers
- Protocol analysis
- Security alerts
- Peak usage hours

## Files

- `backend.py`: Contains functions to get open ports and process information.
- `frontend.py`: Contains the PyQt5 GUI for the Network Task Manager.
- `main.py`: Entry point to run the Network Task Manager.
- `requirements.txt`: Lists the required Python packages.
- `Pipfile`: Lists the required Python packages and their versions for Pipenv.
- `Git Commands.txt`: Contains useful Git commands and instructions.

## Important Notes

- Ensure you have the necessary permissions to run network monitoring commands.
- The tool may require administrative privileges to enable/disable ports.
- Some features (like port blocking) may require running as administrator/root.
- The application creates log files to store network monitoring data.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
