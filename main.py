"""
This is main executable script for SYNCC-IN Eye-tracking during movie stimuli procedure.
Nomenclature:
    - Master is the MSI laptop, running Python script and master Pupil Capture instance.
    - Slave is the Dell laptop, running slave Pupil Capture instance.
    - User is the researcher, running the script
    - Subject is the research subject
    - Subject monitor is the main presentation monitor, seen by the User.
    - ROUTINE -> Code segment, PsychoPy-like structured while loop
    - INTERRUPT -> Code segment, which requires the User intervention
    - VERBATIM -> Code segment, without the need of the User intervention but takes some time
The script function sequence is as follows:
    - PsychoPy log, directory and path setup
    - PsychoPy I/O devices, screen and windows setup
    - Establishing ZMQ connection to both master and slave Pupil instances
    - Creating PsychoPy clocks used during routines and globally
    - Calibration sub-procedure:
        - Show calibration instruction movie to Subjects
        - Calibrate Master Pupil instance
        - Calibrate Slave Pupil instance
        - Redo if needed
    - Recording sub-procedure:
        - Start recording at both Pupil instances
        - Initialize the stimuli (movies, photodiode marker and fixation cross)
        - Stimuli presentation loop:
            - Show movie for 60s
            - Show fixation cross for 10s
            - Continue
        - Stop recording 
    - Saving logs
    - Cleaning up, closing communication ports etc.
"""


# Public Imports
from psychopy import sound, gui, visual, core, data, event, logging, clock, colors, layout, monitors
import psychopy.iohub as io
from psychopy.hardware import keyboard
import ast

# Own Imports
import comms
import procedure_setup
import routines
import pyglet

# GLOBAL PARAMETERS:

WIN_ID_MASTER = 1
WIN_ID_MAIN = 0
WIN_SIZES = [None, None]
WIN_SIZES[WIN_ID_MASTER] = (1920, 1080)
WIN_SIZES[WIN_ID_MAIN] = (2560, 1440)

screens = pyglet.canvas.get_display().get_screens()
"""
for i, screen in enumerate(screens):
    print(f"Screen {i}: {screen.width}x{screen.height}, x={screen.x}, y={screen.y}")
    if screen.width != WIN_SIZES[i][0] or screen.height != WIN_SIZES[i][1]:
        raise TypeError('Screen IDs are wrong!')
"""
CALIB_ANI_1_PATH = 'C://movies_et//norm_kalib_1.mp4'
CALIB_ANI_2_PATH = 'C://movies_et//norm_kalib_2.mp4'
CALIB_ANI_3_PATH = 'C://movies_et//norm_kalib_3.mp4'

MOVIE_1_PATH = 'C://movies_et//norm_mov1.mp4'
MOVIE_2_PATH = 'C://movies_et//norm_mov2.mp4'
MOVIE_3_PATH = 'C://movies_et//norm_mov3.mp4'

### STAGE 1: SETUP

# Specify path for log and data saving
expInfo, thisExp, logFile, filename = procedure_setup.setup_path_log_psychopy()  # creating log files and saving paths
endExpNow = False  # flag for 'escape' or other condition => quit the exp
frameTolerance = 0.005  # how close to onset before 'same' frame

ses_date, ses_time = expInfo['date'][:-7].split('_')
ses_date = ses_date.replace('-', '_')
ses_time = ses_time.replace('h', '')
ses_pupil_file = f"{ses_date}_et_{ses_time}_{expInfo['participant']}"

# Setup windows for procedure
bckgnd_clr_str = expInfo['window background color']  # Get bckgnd color from UI
bckgnd_clr = ast.literal_eval(bckgnd_clr_str)  # Convert it to a list of RGB
win, win_master, gigabyte_mon, test_mon = procedure_setup.setup_windows(win_id_master=WIN_ID_MASTER, win_id_main=WIN_ID_MAIN, background_clr=bckgnd_clr)  # Setup the windows: win is seen on Subject monitor, win_master on Master monitor

# Setup input/output devices - standard PsychoPy segment
ioConfig = {}
ioConfig['Keyboard'] = dict(use_keymap='psychopy')
ioServer = io.launchHubServer(window=win_master, **ioConfig)
defaultKeyboard = keyboard.Keyboard(backend='iohub')
ioSession = '1'
if 'session' in expInfo:
    ioSession = str(expInfo['session'])

# Setup Pupil/Psychopy comms using ZMQ library:
# Creates ZMQ contexts and on this contexts REQ, SUB and PUB channels are established for both PCs. Also makes sure that both PCs have Pupil Capture instances.
context_master, req_master, pub_master, sub_master, context_slave, req_slave, pub_slave, sub_slave = procedure_setup.setup_pupil_comms(wifi_source='hotspot_msi')

# Setup timers
globalClock = core.Clock()  # to track the time since experiment started
routineTimer = core.Clock()  # to track time remaining of each (possibly non-slip) routine

# GUI debugging
if expInfo['debug mode'] == 'True':
    debug_mode = True
else:
    debug_mode = False
start_stage = int(expInfo['start at stage'][0])

### STAGE 2: CALIBRATION

"""
 1. Initialize all calib_ani
 2. User input: start calib_ani_1
 3. Run calib_ani_1, clear window
 4. Change the HDMI input to caregiver -> slave
 5. User input: is HDMI on slave?
 6. Run calibration on caregiver(sl)
 7. Verify that calibration on caregiver is acceptable
 8. Change the HDMI input to child -> master
 9. User input: Is HDMI on master? Should calib_ani_2 start?
 10. Initialize a window
 11. Run calib_ani_2, clear window
 12. Run calibration on child(mast)
 13. Verify that calibration on child is acceptable
 14. User input: Was calibration successful? If yes, run calib_ani_3
 15. Initialize a window
 16. Run calib_ani_3, clear window
"""
# 0. Shortcut:
if start_stage <= 2:

    # 1. VERBATIM: Initialize calibration animations
    calib_anim_1 = visual.MovieStim3(win, CALIB_ANI_1_PATH, size=(2560, 1440))
    print('calib_anim_1 initialized...')

    # 2. INTERRUPT: PRESS X TO BEGIN CALIB INSTRUCTION
    routines.interrupt('Press \'x\' to begin calibration instruction...', win_master)  # This will be seen on the User's screen (win_master)

    # 3. ROUTINE: Calibration animation 1
    ani_components = [calib_anim_1]
    routines.setup_routine_components(ani_components) # Setup psychopy routine for calibration instruction
    comms.send_annotation(pub_master, pub_slave, "start_calib_anim_1", req_master) # ZMQ sends info to Pupil Captures to write to logs that the calibration instruction movie starts
    routines.run_routine(win, ani_components, routineTimer, defaultKeyboard, msg='Running calib_anim_1...', duration=calib_anim_1.duration if not debug_mode else 5)  # Present the instruction
    comms.send_annotation(pub_master, pub_slave, "stop_calib_anim_1", req_master)  # Annotate that animation has stopped
    win.close()  # Clean-up the Subject's window
    del win

    # 4/5. INTERRUPT: HDMI to caregiver(sl)
    routines.interrupt('Press \'x\' when caregiver (sl) monitor input is set...', win_master)

    # 6/7. ROUTINE: Caregiver(sl) calibration
    routines.interrupt('Press \'x\' to begin caregiver (sl) calibration...', win_master)
    if not debug_mode:
        slave_ang, slave_prec = routines.run_calibration(req_slave, sub_slave)  # Run calibration for Slave Subject

    # 8/9. INTERRUPT: HDMI to child
    routines.interrupt('Press \'x\' when child (mast) monitor input is set. This will run second part of calibration instruction', win_master)

    # 10. VERBATIM: Creating a new window on child (master) pc
    win = visual.Window(
        size=[2560, 1440], fullscr=True, screen=WIN_ID_MAIN,
        winType='pyglet', allowStencil=False,
        monitor=gigabyte_mon, color=bckgnd_clr, colorSpace='rgb',
        blendMode='avg', useFBO=True,
        units='height')
    win.flip()
    print('New window created...')

    # 11. ROUTINE: Calibration animation 2
    calib_anim_2 = visual.MovieStim3(win, CALIB_ANI_2_PATH, size=(2560, 1440))
    print('calib_anim_2 initialized...')

    ani_components = [calib_anim_2]
    routines.setup_routine_components(ani_components) # Setup psychopy routine for calibration instruction
    comms.send_annotation(pub_master, pub_slave, "start_calib_anim_2", req_master) # ZMQ sends info to Pupil Captures to write to logs that the calibration instruction movie starts
    routines.run_routine(win, ani_components, routineTimer, defaultKeyboard, msg='Running calib_anim_2...', duration=calib_anim_2.duration if not debug_mode else 5)  # Present the instruction
    comms.send_annotation(pub_master, pub_slave, "stop_calib_anim_2", req_master)  # Annotate that animation has stopped
    win.close()  # Clean-up the Subject's window
    del win

    # 12/13. ROUTINE: Child (master) calibration
    routines.interrupt('Press \'x\' to begin master calibration...', win_master)  # Wait for the User's intervention
    if not debug_mode:
        master_ang, master_prec = routines.run_calibration(req_master, sub_master)  # Run calibration for Master Subject

    # 14. INTERRUPT: Final verification, waiting for calib_ani_3
    routines.interrupt('Press \'x\' if the calibration was successful. This will run the third part of the calibration', win_master)

    # 15. VERBATIM: Creating a new window on child (master) pc
    win = visual.Window(
        size=[2560, 1440], fullscr=True, screen=WIN_ID_MAIN,
        winType='pyglet', allowStencil=False,
        monitor=gigabyte_mon, color=bckgnd_clr, colorSpace='rgb',
        blendMode='avg', useFBO=True,
        units='height')
    win.flip()
    print('New window created...')

    # 16. ROUTINE: Calibration animation 3
    calib_anim_3 = visual.MovieStim3(win, CALIB_ANI_3_PATH, size=(2560, 1440))
    print('calib_anim_3 initialized...')

    ani_components = [calib_anim_3]
    routines.setup_routine_components(ani_components) # Setup psychopy routine for calibration instruction
    comms.send_annotation(pub_master, pub_slave, "start_calib_anim_3", req_master) # ZMQ sends info to Pupil Captures to write to logs that the calibration instruction movie starts
    routines.run_routine(win, ani_components, routineTimer, defaultKeyboard, msg='Running calib_anim_3...', duration=calib_anim_3.duration if not debug_mode else 5)  # Present the instruction
    comms.send_annotation(pub_master, pub_slave, "stop_calib_anim_3", req_master)  # Annotate that animation has stopped
    win.close()  # Clean-up the Subject's window
    del win

### STAGE 3: MOVIES

# 0. Shortcut:
movies = None
if start_stage <= 3:

    win = visual.Window(
        size=[2560, 1440], fullscr=True, screen=WIN_ID_MAIN,
        winType='pyglet', allowStencil=False,
        monitor=gigabyte_mon, color=bckgnd_clr, colorSpace='rgb',
        blendMode='avg', useFBO=True,
        units='height')
    win.flip()
    print('New window created...')

    # VERBATIM: Start recording
    rec_trigger = {'subject': 'recording.should_start', "session_name": ses_pupil_file, "remote_notify": "all"}  # Prepare recording trigger
    comms.notify(req_master, rec_trigger)
    comms.notify(req_slave, rec_trigger)  # Send it to both Pupil Capture Instances
    print("Recording has started")

    # Initializing stimuli
    photo_pos = (1, 0)  # Normalized position of photodiode on the screen
    movies, rand_movies, photo_rect_on, photo_rect_off, cross = procedure_setup.setup_main_stimuli(win, MOVIE_1_PATH, MOVIE_2_PATH, MOVIE_3_PATH, photo_pos=photo_pos)  # Setting up presented movies, photodiode marker and fixation cross
    expInfo['mov_order'] = rand_movies  # Save the order of the movies
    cross.draw()  # Draw focus cross before the first movie
    win.flip()  # Refresh window

    # INTERRUPT: Start main procedure
    routines.interrupt('Press \'x\' to begin stimulus procedure...', win_master)
    win_master.flip() # Refresh window

    # ROUTINE: Movies presentation:
    for i in range(len(rand_movies)):
        # Movie setup
        mov_name = rand_movies[i] # Pick movie
        movie = movies[mov_name] # Pack it into components list
        routines.setup_routine_components([movie]) # Set it up for routine

        # Sending start movie annotation
        comms.send_annotation(pub_master, pub_slave, label=f'start_{str(mov_name)}', req_master=req_master)


        # Running routine
        movie.reset()  # Synchronize audio with video.
        routines.run_stimulus_routine(win, mov_name, movie, photo_rect_on, photo_rect_off, routineTimer,
                                      thisExp, defaultKeyboard, movie_duration=movie.duration-1 if not debug_mode else 10)

        # Sending stop movie annotation
        comms.send_annotation(pub_master, pub_slave, label=f'stop_{str(mov_name)}', req_master=req_master)

        # Setup and present fixation cross between the movies and at the end of movie sequence presentation
        routines.setup_routine_components([cross])
        routines.run_routine(win, [cross], routineTimer, defaultKeyboard, duration=10)

    # VERBATIM: Ending record
    req_master.send_string("r")
    print('Ending recording for master: ' + req_master.recv_string())
    req_slave.send_string("r")
    print('Ending recording for slave: ' + req_slave.recv_string())


### STAGE 4: FREE CONVO
if start_stage <= 4:
    if movies is None:
        photo_rect_on, photo_rect_off = procedure_setup.setup_free_convo_stimuli(win)

    free_convos = ['first', 'second']
    convo_countdown = int(expInfo['free conversation countdown'])
    convo_len = int(expInfo['free conversation length'])
    for i in free_convos:
        routines.interrupt(f'Press \'x\' to begin {i} free conversation...', win_master)

        # VERBATIM: Start recording
        rec_trigger = {'subject': 'recording.should_start', "session_name": ses_pupil_file, "remote_notify": "all"}
        comms.notify(req_master, rec_trigger)
        comms.notify(req_slave, rec_trigger)
        print("Recording has started")

        routines.run_free_convo_routine(win, win_master, photo_rect_on, photo_rect_off,
                                        req_master, pub_master, pub_slave,
                                        convo_countdown, convo_len, routineTimer, thisExp, defaultKeyboard)

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
win_master.close()
core.quit()
