import os
import zmq
import time
import numpy as np

from numpy.random import random, randint, normal, shuffle, choice as randchoice
from psychopy import sound, gui, visual, core, data, event, logging, clock, colors, layout, monitors
import comms
import msgpack
import psychopy.iohub as io
from psychopy.hardware import keyboard

# TODO: Proper argument and return types docstring

def setup_path_log_psychopy():
    """
    Setup paths and logs for ET procedure.

    Returns:
        - expInfo (dict) Dictionary of experiment information (name:value)
        - thisExp (ExperimentHandler) ???
        - logFile (LogFile) ???
        - filename (str) Absolute path for saving all data and logs.
    """

    # Path for saving logs
    _thisDir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(_thisDir)

    # Info about experimental session and what goes into GUI dialog
    psychopyVersion = '2024.2.4'
    expName = 'et_syncc_in_procedure'
    expInfo = {
        'participant': f"{randint(0, 999999):06.0f}",
        'session': '001',
        'window background color': '[0.0, 0.0, 0.0]',
        'free conversation countdown': '30',
        'free conversation length': '180',
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
    # TODO: Create one standardized directory with both recordings and psychopy logs/data

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

def setup_windows(background_clr = None):
    all_monitors = monitors.getAllMonitors()
    print(f"Available monitors: {all_monitors}")

    # Define monitor specifications
    gigabyte_monitor = monitors.Monitor('GIGABYTE')
    gigabyte_monitor.setWidth(52.7)  # Width in cm (adjust for your monitor)
    gigabyte_monitor.setSizePix([2560, 1440])  # Resolution
    gigabyte_monitor.setDistance(57)  # Distance from the screen in cm
    gigabyte_monitor.saveMon()  # Save the monitor configuration

    test_monitor = monitors.Monitor('testMonitor')
    test_monitor.setWidth(30.0)  # Width in cm (adjust for your monitor)
    test_monitor.setSizePix([640, 480])  # Resolution
    test_monitor.setDistance(50)  # Distance from the screen in cm
    test_monitor.saveMon()  # Save the monitor configuration

    if background_clr is None:
        background_clr = [-1.0, -1.0, -1.0]

    win_main = visual.Window(
        size=[2560, 1440], fullscr=True, screen=1,
        winType='pyglet', allowStencil=False,
        monitor=gigabyte_monitor, color=background_clr, colorSpace='rgb',
        blendMode='avg', useFBO=True,
        units='norm')
    win_main.mouseVisible = True

    win_master = visual.Window(
        size=[640, 480], fullscr=False, screen=0,
        winType='pyglet', allowStencil=False,
        monitor=test_monitor, color=background_clr, colorSpace='rgb',
        blendMode='avg', useFBO=True,
        units='norm')
    print("Windows defined")

    return win_main, win_master, gigabyte_monitor, test_monitor

def setup_pupil_comms(wifi_source='hotspot_msi'):

    # Dictionary format: key(wifi name) : tuple(addr_master, addr_slave)
    addr_dict = {
        'hotspot_msi':("127.0.0.1", "192.168.137.100")
    }

    addr_master, addr_slave = addr_dict[wifi_source]

    # Master PC - ports and connections
    port_master = "50020"
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
    port_slave = "50020"
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

    # Master PC - plugins
    # sub.setsockopt_string(zmq.SUBSCRIBE, 'notify.calibration')
    # Starting master plugins / "Time_Sync" - important for synchronising pupil cores, base_bias - higher value defines master
    comms.notify(req_master, {"subject": "start_plugin", "name": "Annotation_Capture", "args": {}})
    comms.notify(req_master,
                 {"subject": "start_plugin", "name": "Time_Sync",
                  "args": {'base_bias': 1.1, 'node_name': 'sync_master'}})
    comms.notify(req_master, {"subject": "start_plugin", "name": "Log_History", "args": {}})
    comms.notify(req_master,
                 {"subject": "start_plugin", "name": "Pupil_Groups",
                  "args": {'name': 'master_pupil', 'active_group': 'ET_exp'}})

    # Slave PC - plugins
    # sub.setsockopt_string(zmq.SUBSCRIBE, 'notify.calibration')

    # Starting slave plugins
    comms.notify(req_slave, {"subject": "start_plugin", "name": "Annotation_Capture", "args": {}})
    comms.notify(req_slave,
                 {"subject": "start_plugin", "name": "Time_Sync",
                  "args": {'base_bias': 1.0, 'node_name': 'sync_slave'}})
    comms.notify(req_slave, {"subject": "start_plugin", "name": "Log_History", "args": {}})
    comms.notify(req_slave,
                 {"subject": "start_plugin", "name": "Pupil_Groups",
                  "args": {'name': 'slave_pupil', 'active_group': 'ET_exp'}})

    # TODO: to mozna logowac, a moze nawet zrobic check latencji
    t = time.time()
    req_master.send_string("t")
    req_master.recv_string()
    print("Round trip Python<->Pupil command delay:", time.time() - t)

    req_master.send_string("T 0.0")
    print(f'Master timesync: {req_master.recv_string()}')
    req_slave.send_string("T 0.0")
    print(f'Slave timesync: {req_slave.recv_string()}')

    print('Pupil Communication established.')

    return context_master, req_master, pub_master, sub_master, context_slave, req_slave, pub_slave, sub_slave

def setup_main_stimuli(win, vid1_path, vid2_path, vid3_path, photo_pos=(1, 0)):
    # Stim init
    print('Initializing stimuli...')
    movie_1 = visual.MovieStim3(win, vid1_path, size=(2560, 1440))
    print('m1 initialized...')
    movie_2 = visual.MovieStim3(win, vid2_path, size=(2560, 1440))
    print('m2 initialized...')
    movie_3 = visual.MovieStim3(win, vid3_path, size=(2560, 1440))
    print('m3 initialized...')
    movies = {'m1': movie_1, 'm2': movie_2, 'm3': movie_3}
    rand_movies = list(np.random.permutation(list(movies.keys())))

    # Photodiode rectangle init
    size = 0.1
    photo_rect_on = visual.Rect(
        win=win, name='photo_rect_on',
        width=size * (9 / 16), height=size, units='norm',
        ori=0.0, pos=photo_pos, anchor='bottom-right',
        lineWidth=1.0, colorSpace='rgb', lineColor='white', fillColor='white',
        opacity=None, depth=0.0, interpolate=True)

    size = 0.1
    photo_rect_off = visual.Rect(
        win=win, name='photo_rect_off',
        width=size * (9 / 16), height=size, units='norm',
        ori=0.0, pos=photo_pos, anchor='bottom-right',
        lineWidth=1.0, colorSpace='rgb', lineColor='black', fillColor='black',
        opacity=None, depth=0.0, interpolate=True)

    # Cross stimuli init
    cross = visual.ShapeStim(
        win=win,
        vertices='cross',  # Define shape as a cross
        size=(2,2),  # Size of the cross (width and height)
        lineWidth=1,  # Line thickness
        lineColor='black',  # Line color (white)
        fillColor='black',  # Fill color (white)
        units='cm',  # Use normalized units
        pos=(0, 0)  # Center of the screen
        )
    photo_rect_off.draw()
    win.flip()
    return movies, rand_movies, photo_rect_on, photo_rect_off, cross

def setup_free_convo_stimuli(win, photo_pos=(1, 0)):

    # Photodiode rectangle init
    size = 0.1
    photo_rect_on = visual.Rect(
        win=win, name='photo_rect_on',
        width=size * (9 / 16), height=size, units='norm',
        ori=0.0, pos=photo_pos, anchor='bottom-right',
        lineWidth=1.0, colorSpace='rgb', lineColor='white', fillColor='white',
        opacity=None, depth=0.0, interpolate=True)

    size = 0.1
    photo_rect_off = visual.Rect(
        win=win, name='photo_rect_off',
        width=size * (9 / 16), height=size, units='norm',
        ori=0.0, pos=photo_pos, anchor='bottom-right',
        lineWidth=1.0, colorSpace='rgb', lineColor='black', fillColor='black',
        opacity=None, depth=0.0, interpolate=True)


    photo_rect_off.draw()
    win.flip()
    return photo_rect_on, photo_rect_off