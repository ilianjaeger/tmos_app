import serial
import time
import numpy as np
import threading
from datetime import datetime
import argparse
import time
import sys
import logging

from lib import PIR
from lib import comm_interface

# Initialize logger
logging.basicConfig(
    level=logging.INFO,
    format='[%(name)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Start logger
logger = logging.getLogger('PC.MAIN')
logger.setLevel(logging.INFO)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='STM32 Serial')
    parser.add_argument('-p', '--port_name', type=str, choices=comm_interface.list_available_ports(), help='The port to be opened', required=True)
    parser.add_argument('-m', '--stream_m', type=str, choices={"0", "1"}, help='0 - slow, 1 - fast', required=True)
    args = parser.parse_args()

    logging.info("----- STARTING OUR COOL PROGRAM -----\n")

    comm = comm_interface.SerialInterface(args.stream_m)
    if comm.open_port(args.port_name) == False:
        logging.error("An error occurred while opening the port. Closing...")
        exit()

    comm.connect_device()

    logger.info("Starting main loop")

    # Main loop
    while True:
        rec = comm.read_text()
        if rec is not '':
            logger.info(rec)