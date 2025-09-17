"""
Setup for logging paths, screens, windows, PsychoPy handlers, Pupil Capture communication and presented stimuli.
"""
import os
import zmq
import time
from numpy.random import randint
from psychopy import  gui, visual, core, data, logging, monitors

import m03_pupilcapture_comms as comms

from config import FREE_CONV_DURATION, FREE_CONV_INTERVAL, DEFAULT_BCKGND, PHOTODIODE_POS
from config import WIN_ID_MAIN, WIN_ID_MASTER, WIN_SIZES
from config import WIFI_IP_DICT, WIFI_SOURCE, MASTER_PORT, SLAVE_PORT

def setup_path_log_psychopy():
    """
    Setup paths and logs for ET procedure.

    Returns:
        - expInfo (dict): Dictionary of experiment information (name:value)
        - thisExp (ExperimentHandler): PsychoPy handler.
        - logFile (LogFile): PsychoPy logfile.
        - filename (str) Absolute path for saving all data and logs.
    """

    # Path for saving logs
    _thisDir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(_thisDir)

    # Info about experimental session and what goes into GUI dialog
    psychopyVersion = '2025.1.1'
    expName = 'et_syncc_in_procedure'
    expInfo = {
        'participant': f"{randint(0, 999999):06.0f}",
        'session': '001',
        'window background color': str(DEFAULT_BCKGND),
        'free conversation countdown': str(FREE_CONV_INTERVAL),
        'free conversation length': str(FREE_CONV_DURATION),
        'debug mode': ['False', 'True'],
        'start at stage': ['2. Calibration', '3. Movies', '4. Free convo']
    }
    print(f"Syncc-In ET procedure, participant: {expInfo['participant']}")

    # Participant info dialog
    session_win = True
    if session_win:
        dlg = gui.DlgFromDict(dictionary=expInfo, sortKeys=False, title=expName)
        if not dlg.OK:
            core.quit()  # user pressed cancel
    expInfo['date'] = data.getDateStr()  # add a simple timestamp
    expInfo['expName'] = expName
    expInfo['psychopyVersion'] = psychopyVersion

    # Data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
    filename = _thisDir + os.sep + u'data/%s_%s_%s' % (expInfo['participant'], expName, expInfo['date'])

    # An ExperimentHandler isn't essential but helps with data saving
    thisExp = data.ExperimentHandler(name=expName, version='',
                                     extraInfo=expInfo, runtimeInfo=None,
                                     originPath='C:\\Users\\Badania\\PycharmProjects\\et_procedure',
                                     savePickle=True, saveWideText=True,
                                     dataFileName=filename)
    # save a log file for detail verbose info
    logFile = logging.LogFile(filename + '.log', level=logging.EXP)
    logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file

    return expInfo, thisExp, logFile, filename

def setup_windows(background_clr:tuple|list = None):
    """
    Creates PsychoPy-based windows used during procedure.

    Args:
        background_clr (tuple|list) : RGB backround color

    Returns:
        win_main (Window): PsychoPy window, presented to the Subjects.
        win_master (Window): PsychoPy window, used by the Researcher.
        gigabyte_monitor (Monitor): PsychoPy Monitor - main, presented to the Subjects.
        test_monitor (Monitor): PsychoPy Monitor - master PC monitor.

    """

    all_monitors = monitors.getAllMonitors()
    print(f"Available monitors: {all_monitors}")

    # monitor specs
    gigabyte_monitor = monitors.Monitor('GIGABYTE')
    gigabyte_monitor.setWidth(52.7)
    gigabyte_monitor.setSizePix(WIN_SIZES[WIN_ID_MAIN])
    gigabyte_monitor.setDistance(65)
    gigabyte_monitor.saveMon()

    test_monitor = monitors.Monitor('testMonitor')
    test_monitor.setWidth(30.0)
    test_monitor.setSizePix([640, 480])
    test_monitor.setDistance(50)
    test_monitor.saveMon()

    if background_clr is None:
        background_clr = [-1.0, -1.0, -1.0]

    win_main = visual.Window(
        size=WIN_SIZES[WIN_ID_MAIN], fullscr=True, screen=WIN_ID_MAIN,
        winType='pyglet', allowStencil=False,
        monitor=gigabyte_monitor, color=background_clr, colorSpace='rgb',
        blendMode='avg', useFBO=True,
        units='norm', infoMsg='.')
    win_main.mouseVisible = True

    win_master = visual.Window(
        size=[640, 480], fullscr=False, screen=WIN_ID_MASTER,
        winType='pyglet', allowStencil=False,
        monitor=test_monitor, color=background_clr, colorSpace='rgb',
        blendMode='avg', useFBO=True,
        units='norm', infoMsg='.')
    print("Windows defined")

    return win_main, win_master, gigabyte_monitor, test_monitor

def setup_pupil_comms():
    """
    Setup for Python <-> PupilCapture communications.
    Sends appropriate settings to the PupilCapture instances.
    Creates PUB, SUB and REQ sockets for bot slave and master Pupil instances.
    Based on ZMQ library.

    Returns:
         context_master (zmq.Context): Context for Master PC.
         req_master (zmq.Socket): REQ socket on Master context.
         pub_master (zmq.Socket): PUB socket on Master context.
         sub_master (zmq.Socket): SUB socket on Master context.
         context_slave (zmq.Context): Context for Slave PC.
         req_slave (zmq.Socket): REQ socket on Slave context.
         pub_slave (zmq.Socket): SUB socket on Slave context.
         sub_slave (zmq.Socket): PUB socket on Slave context.

    """

    addr_master, addr_slave = WIFI_IP_DICT[WIFI_SOURCE]

    # Master PC - ports and connections
    port_master = str(MASTER_PORT)
    comms.check_capture_exists(addr_master, port_master, 'Master')

    context_master = zmq.Context()  # Context creation
    context_master.setsockopt(zmq.LINGER, 0)

    req_master = context_master.socket(zmq.REQ)  # Master req
    req_master.connect("tcp://{}:{}".format(addr_master, port_master))

    # pub: send info to other processes - we use it to send annotations to pupil capture
    req_master.send_string("PUB_PORT")  # Master pub
    pub_port_master = req_master.recv_string()
    pub_master = zmq.Socket(context_master, zmq.PUB)
    pub_master.connect("tcp://{}:{}".format(addr_master, pub_port_master))

    # sub: listen to other processes - currently listens to the calibration parameters from pupil capture
    req_master.send_string("SUB_PORT")  # Master sub
    sub_port_master = req_master.recv_string()
    sub_master = context_master.socket(zmq.SUB)
    sub_master.connect("tcp://{}:{}".format(addr_master, sub_port_master))
    sub_master.setsockopt_string(zmq.SUBSCRIBE, 'logging')
    print("Master ports established")

    # Slave PC - ports and connections
    port_slave = str(SLAVE_PORT)
    comms.check_capture_exists(addr_slave, port_slave, 'Slave')

    context_slave = zmq.Context()  # Context creation

    req_slave = context_slave.socket(zmq.REQ)  # Slave req
    req_slave.connect("tcp://{}:{}".format(addr_slave, port_slave))

    req_slave.send_string("PUB_PORT")  # Slave pub
    pub_port_slave = req_slave.recv_string()
    pub_slave = zmq.Socket(context_slave, zmq.PUB)
    pub_slave.connect("tcp://{}:{}".format(addr_slave, pub_port_slave))

    req_slave.send_string("SUB_PORT")  # Slave sub
    sub_port_slave = req_slave.recv_string()
    sub_slave = context_slave.socket(zmq.SUB)
    sub_slave.connect("tcp://{}:{}".format(addr_slave, sub_port_slave))
    sub_slave.setsockopt_string(zmq.SUBSCRIBE, 'logging')
    print("Slave ports established")

    # Safety-check: Stop recording if there is one.
    rec_trigger = {'subject': 'recording.should_stop', "remote_notify": "all"}
    comms.notify(req_master, rec_trigger)
    comms.notify(req_slave, rec_trigger)

    # Master PC - plugins: Annotation_Capture, Time_Sync, Log_History, Pupil_Groups
    comms.notify(req_master,
                 {"subject": "start_plugin", "name": "Annotation_Capture", "args": {}})
    comms.notify(req_master,
                 {"subject": "start_plugin", "name": "Time_Sync",
                  "args": {'base_bias': 1.1, 'node_name': 'sync_master'}})
    comms.notify(req_master,
                 {"subject": "start_plugin", "name": "Log_History", "args": {}})
    comms.notify(req_master,
                 {"subject": "start_plugin", "name": "Pupil_Groups",
                  "args": {'name': 'master_pupil', 'active_group': 'ET_exp'}})

    # Slave PC - plugins: Annotation_Capture, Time_Sync, Log_History, Pupil_Groups
    comms.notify(req_slave,
                 {"subject": "start_plugin", "name": "Annotation_Capture", "args": {}})
    comms.notify(req_slave,
                 {"subject": "start_plugin", "name": "Time_Sync",
                  "args": {'base_bias': 1.0, 'node_name': 'sync_slave'}})
    comms.notify(req_slave,
                 {"subject": "start_plugin", "name": "Log_History", "args": {}})
    comms.notify(req_slave,
                 {"subject": "start_plugin", "name": "Pupil_Groups",
                  "args": {'name': 'slave_pupil', 'active_group': 'ET_exp'}})

    # Time synchronization and comms delay.
    t = time.time()
    req_master.send_string("t")
    req_master.recv_string()
    python_to_pupil_delay = time.time() - t
    print("Round trip Python<->Pupil command delay:", python_to_pupil_delay)

    req_master.send_string("T 0.0")
    print(f'Master timesync: {req_master.recv_string()}')
    req_slave.send_string("T 0.0")
    print(f'Slave timesync: {req_slave.recv_string()}')

    print('Pupil Communication established.')

    return context_master, req_master, pub_master, sub_master, context_slave, req_slave, pub_slave, sub_slave

def setup_photodiode(win, photo_pos=PHOTODIODE_POS):
    """
    Setup for photodiode crude communications - blinking black-and-white box, registered by photodiode connected to EEG.
    Also creates the fixation cross.

    Args:
        win (Window): Main PsychoPy window.
        photo_pos: Normalized box position on the win.

    Returns:
        photo_rect_on (visual.Rect): Onset photodiode rectangle - white box.
        photo_rect_off (visual.Rect): Offset photodiode rectangle - blackbox.
        cross (visual.ShapeStim): Fixation cross.
    """

    # Photodiode rectangle init
    size = 0.1
    photo_rect_on = visual.Rect(
        win=win, name='photo_rect_on',
        width=size * (9 / 16), height=size, units='norm',
        ori=0.0, pos=photo_pos, anchor='bottom-right',
        lineWidth=1.0, colorSpace='rgb',
        lineColor='white', fillColor='white',
        opacity=None, depth=0.0, interpolate=True)

    size = 0.1
    photo_rect_off = visual.Rect(
        win=win, name='photo_rect_off',
        width=size * (9 / 16), height=size, units='norm',
        ori=0.0, pos=photo_pos, anchor='bottom-right',
        lineWidth=1.0, colorSpace='rgb',
        lineColor='black', fillColor='black',
        opacity=None, depth=0.0, interpolate=True)

    # Cross stimuli init
    cross = visual.ShapeStim(
        win=win,
        vertices='cross',
        size=(2,2),
        lineWidth=1,
        lineColor='black',
        fillColor='black',
        units='cm',
        pos=(0, 0)
        )
    photo_rect_off.draw() # draw black-box immediately
    win.flip()
    return photo_rect_on, photo_rect_off, cross
