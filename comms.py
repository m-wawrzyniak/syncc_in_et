import zmq
import msgpack as serializer
import socket
import sys

# TODO: Properly defined argument types and return types

def notify(pupil_remote, notification: dict):
    """
    Prepares payload to sent using notification (dict) and sends it
    to pupil_remote (Context.socket).
    """
    topic = "notify." + notification["subject"]
    payload = serializer.dumps(notification, use_bin_type=True)
    pupil_remote.send_string(topic, flags=zmq.SNDMORE)
    pupil_remote.send(payload)
    return pupil_remote.recv_string()

def send_trigger(pub_socket, trigger):
    """
    Sends a trigger (dict) via PUB socket (Context.socket())
    """
    payload = serializer.dumps(trigger, use_bin_type=True)
    pub_socket.send_string(trigger["topic"], flags=zmq.SNDMORE)
    pub_socket.send(payload)

def check_capture_exists(ip_address, port, pc):
    """
    Check if Pupil Capture instance exists at specific PC with ip_address via port
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        if not sock.connect_ex((ip_address, int(port))):
            print(f"{pc}: Found Pupil Capture")
        else:
            print("{pc}: Cannot find Pupil Capture")
            sys.exit()

def send_annotation(pub_master, pub_slave, label, req_master):
    """
    Send annotation (string) to both slave and master pc via PUB sockets (Context.socket),
    including also Master Pupil Capture time based on Master clock.
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
