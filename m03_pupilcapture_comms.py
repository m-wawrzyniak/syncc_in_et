"""
Handling PupilCapture instances communications.
"""

import zmq
import msgpack as serializer
import socket
import sys
from zmq.asyncio import Socket


def notify(pupil_remote:Socket, notification:dict):
    """
    Prepares payload to sent using notification (dict) and sends it
    to pupil_remote (Context.socket).

    Args:
        pupil_remote (Socket): Target ZMQ socket.
        notification (dict): Notification content.

    Returns:
        (str) - received message from target socket.

    """
    topic = "notify." + notification["subject"]
    payload = serializer.dumps(notification, use_bin_type=True)
    pupil_remote.send_string(topic, flags=zmq.SNDMORE)
    pupil_remote.send(payload)
    return pupil_remote.recv_string()

def send_trigger(pub_socket:Socket, trigger:dict):
    """
    Sends a trigger (dict) via PUB socket (Context.socket())

    Args:
        pub_socket (Socket): Target socket.
        trigger (dict): Trigger content.
    """
    payload = serializer.dumps(trigger, use_bin_type=True)
    pub_socket.send_string(trigger["topic"], flags=zmq.SNDMORE)
    pub_socket.send(payload)

def check_capture_exists(ip_address:str, port:str, pc:str):
    """
    Check if Pupil Capture instance exists at specific PC with ip_address via port

    Args:
        ip_address (str): Network PC ip address.
        port (str): Network PC port.
        pc (str): String representation of the PC, purely verbose.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        if not sock.connect_ex((ip_address, int(port))):
            print(f"{pc}: Found Pupil Capture")
        else:
            print(f"{pc}: Cannot find Pupil Capture")
            sys.exit()

def send_annotation(pub_master:Socket, pub_slave:Socket, label:str, req_master:Socket):
    """
    Send annotation (string) to both slave and master pc via PUB sockets (Context.socket),
    including also Master Pupil Capture time based on Master clock.

    Args:
        pub_master (Socket): PUB socket for Master PC PupilCapture instance.
        pub_slave (Socket): PUB socket for Slave PC PupilCapture instance.
        label (str): Trigger label.
        req_master (Socket): REQ socket for Master PC PupilCapture instance.
    """
    req_master.send_string('t')
    pupil_time = req_master.recv()
    trigger = {
        "topic": "annotation",
        "label": label,
        "timestamp": float(pupil_time),
        "duration": 0.0,
    }
    send_trigger(pub_master, trigger)
    send_trigger(pub_slave, trigger)
