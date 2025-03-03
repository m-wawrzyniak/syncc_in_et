# Public Imports
from psychopy import sound, gui, visual, core, data, event, logging, clock, colors, layout
import psychopy.iohub as io
from psychopy.hardware import keyboard
import ast

# Own Imports
import comms
import procedure_setup
import routines

# SETUP:

# Specify path for log and data saving
expInfo, thisExp, logFile, filename = procedure_setup.setup_path_and_log()
endExpNow = False  # flag for 'escape' or other condition => quit the exp
frameTolerance = 0.005  # how close to onset before 'same' frame

# Setup windows for procedure
bckgnd_clr_str = expInfo['window background color']  # Get bckgnd color from UI
bckgnd_clr = ast.literal_eval(bckgnd_clr_str)  # Convert it to a list of RGB
win, win_master, gigabyte_mon, test_mon = procedure_setup.setup_windows(background_clr=bckgnd_clr)  # Setup the windows

# Setup input/output devices
ioConfig = {}
ioConfig['Keyboard'] = dict(use_keymap='psychopy')
ioServer = io.launchHubServer(window=win, **ioConfig)
defaultKeyboard = keyboard.Keyboard(backend='iohub')
ioSession = '1'
if 'session' in expInfo:
    ioSession = str(expInfo['session'])

# Setup Pupil/Psychopy comms
context_master, req_master, pub_master, sub_master, context_slave, req_slave, pub_slave, sub_slave = procedure_setup.setup_pupil_comms()

# Setup timers
globalClock = core.Clock()  # to track the time since experiment started
routineTimer = core.Clock()  # to track time remaining of each (possibly non-slip) routine


# INTERRUPT: PRESS X TO BEGIN CALIB INSTRUCTION
routines.interrupt('Press \'x\' to begin calibration instruction...', win_master)

# ROUTINE: CALIB gANIMATION
calib_ani = visual.MovieStim3(win, 'C://Users//Badania//OneDrive//Pulpit//Syncc-In//calib_intro_20.wmv',
                             size=(2560, 1440))
ani_components = [calib_ani]

routines.setup_routine_components(ani_components)
comms.send_annotation(pub_master, pub_slave, "start_calib_animation", req_master)
routines.run_routine(win, ani_components, routineTimer, defaultKeyboard, msg='Running calib animation...', duration=10)
comms.send_annotation(pub_master, pub_slave, "stop_calib_animation", req_master)
win.close()
del win

# INTERRUPT : Calibration
# Master calibration
routines.interrupt('Press \'x\' to begin master calibration...', win_master)
# master_ang, master_prec = routines.run_calibration(req_master, sub_master)
# Slave calibration
routines.interrupt('Press \'x\' to begin slave calibration...', win_master)
#slave_ang, slave_prec = routines.run_calibration(req_slave, sub_slave)

# INTERRUPT: Set master monitor as main
routines.interrupt('Press \'x\' when master monitor input is set...', win_master)

# INTERRUPT: Start recording
rec_trigger = {'subject': 'recording.should_start', "remote_notify": "all"}
comms.notify(req_master, rec_trigger)
comms.notify(req_slave, rec_trigger)
print("Recording has started")

# VERBATIM: Opening new window on main monitor and initializing stimuli
win = visual.Window(
    size=[2560, 1440], fullscr=True, screen=1,
    winType='pyglet', allowStencil=False,
    monitor=gigabyte_mon, color=bckgnd_clr, colorSpace='rgb',
    blendMode='avg', useFBO=True,
    units='height')
win.flip()
print('New window created...')

# Initializing stimuli
photo_pos = (1, 0)  # Normalized position of photodiode on the screen
movies, rand_movies, photo_rect_on, photo_rect_off, cross = procedure_setup.setup_main_stimuli(win, photo_pos=photo_pos)
expInfo['mov_order'] = rand_movies
cross.draw()  # Draw focus cross before the first movie
win.flip()  # Refresh window

# INTERRUPT: Start main procedure
routines.interrupt('Press \'x\' to begin stimulus procedure...', win_master)
win.flip() # Refresh window

# ROUTINE: Movies presentation

for i in range(len(rand_movies)):
    # Movie setup
    mov_name = rand_movies[i] # Pick movie
    movie = movies[mov_name] # Pack it into components list
    routines.setup_routine_components([movie]) # Set it up for routine
    movie.reset()  # Synchronizuje audio z video

    # Sending start movie annotation
    comms.send_annotation(pub_master, pub_slave, label=f'start_{str(mov_name)}', req_master=req_master)

    # Running routine
    routines.run_stimulus_routine(win, mov_name, movie, photo_rect_on, photo_rect_off, routineTimer,
                                  thisExp, defaultKeyboard, movie_duration=movie.duration)

    # Sending stop movie annotation
    comms.send_annotation(pub_master, pub_slave, label=f'stop_{str(mov_name)}', req_master=req_master)

    routines.setup_routine_components([cross])
    routines.run_routine(win, [cross], routineTimer, defaultKeyboard, duration=10)

# VERBATIM: Ending record
req_master.send_string("r")
print('Ending recording for master: ' + req_master.recv_string())
req_slave.send_string("r")
print('Ending recording for slave: ' + req_slave.recv_string())

# VERBATIM: Closing ports
req_master.close()
pub_master.close()
sub_master.close()
req_slave.close()
pub_slave.close()
sub_slave.close()
context_master.destroy()
context_slave.destroy()

# VERBATIM: Saving logs and closing procedure
# thisExp.saveAsWideText(filename + '.csv', delim='auto')  # CSV doesn't save ExpInfo as supposed
thisExp.saveAsPickle(filename)
logging.flush()
thisExp.abort()  # This will cancel ExperimentHandler save during core.quit()
win.close()
core.quit()
