# Basic Network Monitoring

A simple network monitoring tool that detects open ports and their associated processes. It also provides a GUI for monitoring and managing network tasks.

## Requirements

- Python 3.11+
- PyQt5
- psutil

## Installation

1. Clone the repository.
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

## Files

- `backend.py`: Contains functions to get open ports and process information.
- `frontend.py`: Contains the PyQt6 GUI for the Network Task Manager.
- `main.py`: Entry point to run the Network Task Manager.
- `requirements.txt`: Lists the required Python packages.
- `Pipfile`: Lists the required Python packages and their versions for Pipenv.
- `Git Commands.txt`: Contains useful Git commands and instructions.

## Important Notes

- Ensure you have the necessary permissions to run network monitoring commands.
- The tool may require administrative privileges to enable/disable ports.
