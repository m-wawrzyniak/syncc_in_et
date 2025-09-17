"""
Contains full PsychoPy-like procedures.
"""

from psychopy import core, visual, event, sound
from psychopy.constants import NOT_STARTED, STARTED, FINISHED
import msgpack as serializer
from zmq.asyncio import Socket

import m03_pupilcapture_comms as comms

from config import FRAMETOLERANCE


def setup_routine_components(components:list):
    """
    General function for initializing routine components.

    Args:
        components (list): List of PsychoPy components e.g. visual.MovieStim etc.
    """
    for comp in components:
        comp.tStart = None
        comp.tStop = None
        comp.tStartRefresh = None
        comp.tStopRefresh = None
        if hasattr(comp, 'status'):
            comp.status = NOT_STARTED

def run_routine(
    win,
    routine_components,
    routine_timer,
    defaultKeyboard,
    msg="Running routine...",
    duration=None,
    escape_key="escape",
):
    """
    Runs a PsychoPy routine segment:
      win                - (psychopy.visual.Window) window to draw on
      routine_components - (list) PsychoPy stimuli (TextStim, MovieStim, etc.)
      routine_timer      - (psychopy.core.Clock) clock controlling routine
      defaultKeyboard    - (psychopy.hardware.keyboard.Keyboard) keyboard for quit key
      msg                - (str) debug message
      duration           - (float|None) routine duration (s), None = until all comps finish
      escape_key         - (str) key to abort routine
    """
    print(msg)

    continue_routine = True
    frameN = -1
    routine_timer.reset()
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")

    while continue_routine:
        # get current time
        t = routine_timer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routine_timer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN += 1

        # update/draw components
        for comp in routine_components:
            # start routine
            if comp.status == NOT_STARTED and tThisFlip >= 0.0 - FRAMETOLERANCE:
                comp.frameNStart = frameN
                comp.tStart = t
                comp.tStartRefresh = tThisFlipGlobal
                win.timeOnFlip(comp, "tStartRefresh")
                comp.setAutoDraw(True)
                comp.status = STARTED

            # stop routine after duration
            if comp.status == STARTED and duration and t >= duration - FRAMETOLERANCE:
                comp.tStop = t
                comp.frameNStop = frameN
                comp.setAutoDraw(False)
                if isinstance(comp, visual.MovieStim):
                    comp.stop()
                comp.status = FINISHED

        # escape handling
        if defaultKeyboard.getKeys(keyList=[escape_key]):
            for comp in routine_components:
                if isinstance(comp, visual.MovieStim):
                    comp.stop()
            core.quit()

        # continue if some components are still STARTED
        continue_routine = any(
            hasattr(comp, "status") and comp.status == STARTED
            for comp in routine_components
        )

        if continue_routine:
            win.flip()

    # cleanup
    for comp in routine_components:
        if hasattr(comp, "setAutoDraw"):
            comp.setAutoDraw(False)
        if isinstance(comp, visual.MovieStim):
            comp.stop()

def interrupt(msg:str, win:visual.Window, keys:tuple=('x',)):
    """
    Prints msg (str) at win (psychopy.visual.Window) and waits for the User to press on of the keys (tuple)
    Args:
        msg (str): Text message shown at Master PC PsychoPy window.
        win (visual.Window): Window.
        keys (tuple): User input keys.
    """
    print(msg)
    message = visual.TextStim(win, text=msg, color='white')
    message.draw()
    win.flip()
    _ = event.waitKeys(keyList=keys)
    win.flip()

def run_calibration(req_port:Socket, sub_port:Socket, debug_mode:bool=False):
    """
    Runs calibration at specific PC, based on chosen req_port and sub_port (Context.socket).
    Evaluates whether the calibration quality is satisfactory and gives the User a choice to accept the quality
    or redo the calibration.
    debug_mode = True -> there is only a dummy calibration

    Args:
        req_port (zmq.Socket): REQ socket for specific PC PupilCapture instance.
        sub_port (zmq.Socket): SUB socket for specific PC PupilCapture instance.
        debug_mode (bool): Debug mode - no calibration started at PupilCapture.

    Returns:
        ang_acc (float): Resulting angular accuracy of ET after the calibration.
        ang_prec (float): Resulting angular precision of ET after the calibration.

    """
    calib_done = False
    ang_acc, ang_prec = 0, 0

    if not calib_done:
        req_port.send_string("C")
        print(req_port.recv_string(), flush=True)

    while not calib_done:
        topic = sub_port.recv_string()
        msg = sub_port.recv()
        msg = serializer.loads(msg, raw=False)
        if debug_mode:
            print("\n{}: {}".format(topic, msg))

        if 'Angular accuracy' in msg['msg']:
            print(msg['msg'])
            ang_acc = float(msg['msg'].split(' ')[2])
        if 'Angular precision' in msg['msg']:
            print(msg['msg'])
            ang_prec = float(msg['msg'].split(' ')[2])

        if ang_acc and ang_prec:
            if ang_acc < 0.5 and ang_prec < 0.1:
                print('Calibration done')
                calib_done = True
            else:
                print('Accuracy parameters invalid:\nPress \"y\" to redo calbration, press \"n\" to continue')
                while True:
                    keys = event.getKeys()
                    if 'y' in keys:
                        ang_acc, ang_prec = 0, 0
                        print('Redoing calibration')
                        req_port.send_string("C")
                        print(req_port.recv_string())
                        break
                    elif 'n' in keys:
                        print('Finishing calibration with non-optimal accuracy')
                        calib_done = True
                        break
                continue
    return ang_acc, ang_prec

def run_stimulus_routine(win, mov_name, movie, photo_rect_on, photo_rect_off, routineTimer, thisExp, defaultKeyboard,
                         movie_duration=None):
    """
    Movie stimulus presentation routine.
    Using specific window 'win' (psychopy.visual.Window), creates routine segment with predefined stimuli:
    movies, photodiode marker and fixation cross.

    Args:
        win (Window): Window at which the stimulus will be presented.
        mov_name (str): Name of the movie.
        movie (visual.MovieStim): PsychoPy movie stimulus.
        photo_rect_on (visual.Rect): Photodiode onset marker.
        photo_rect_off (visual.Rect): Photodiode offset marker.
        routineTimer (psychopy.core.Clock): PsychoPy routine clock.
        thisExp (dict): PsychoPy log dictionary.
        defaultKeyboard (psychopy.keyboard.Keyboard): Keyboard used for User interface.
        movie_duration (int|None): How long the routine will be run. If None, it will be played as long as the movie.
    """

    continueRoutine = True
    t = 0
    frameN = -1
    routineTimer.reset()
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    if movie_duration is None:
        movie_duration = movie.duration

    # Photodiode setup
    photo_toggle_time = 0.5
    last_toggle_time = 0
    toggle_cnt = 0
    movie_id = int(mov_name[-1])
    photo_is_on = False

    while continueRoutine:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1

        # routine start
        if movie.status == NOT_STARTED and tThisFlip >= 0.0 - FRAMETOLERANCE:
            movie.frameNStart = frameN
            movie.tStart = t  # local time
            movie.tStartRefresh = tThisFlipGlobal  # global time
            win.timeOnFlip(movie, 'tStartRefresh')  # time at next scr refresh
            thisExp.timestampOnFlip(win, '{}.started'.format(mov_name))  # add timestamp to datafile
            movie.setAutoDraw(True)
        # routine started
        if movie.status == STARTED:
            # if duration is exceeded, stop autodraw
            if tThisFlipGlobal > movie.tStartRefresh + movie_duration - FRAMETOLERANCE:
                movie.tStop = t
                movie.frameNStop = frameN
                thisExp.timestampOnFlip(win, '{}.stopped'.format(mov_name))
                movie.setAutoDraw(False)

        # photodiode communication - toggle count is equal to movie ID!
        if (tThisFlipGlobal >= last_toggle_time + photo_toggle_time) and (toggle_cnt <= movie_id * 2):
            last_toggle_time = tThisFlipGlobal
            if not photo_is_on:
                photo_rect_on.setAutoDraw(True)
                photo_rect_off.setAutoDraw(False)
            else:
                photo_rect_on.setAutoDraw(False)
                photo_rect_off.setAutoDraw(True)
            photo_is_on = not photo_is_on
            toggle_cnt += 1

        # escape handling
        if defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()

        # breaking the routine
        if not continueRoutine:
            break
        continueRoutine = False
        for thisComponent in [movie]:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()

    # END MOV ROUTINE
    print('{} finished'.format(mov_name))
    for thisComponent in [movie]:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    movie.stop()
    routineTimer.reset()
    photo_rect_on.setAutoDraw(False)
    photo_rect_off.setAutoDraw(True)

def _show_countdown(duration, win, timer, text_stim, text_content, key_list: tuple = ("escape",)):
    """
    Countdown handler used in free conversation routine.

    Args:
        duration (int):
        win (Window):
        timer (psychopy.core.Clock):
        text_stim (visual.Text):
        text_content (str):
        key_list (tuple):

    Returns:
        None|str

    """
    timer.reset()
    while timer.getTime() < duration:
        remaining = int(duration - timer.getTime())
        text_stim.text = f"{text_content}: {remaining} s"
        text_stim.draw()
        win.flip()

        keys = event.getKeys(keyList=key_list)
        if "escape" in keys:
            core.quit()
        elif "x" in keys:
            return "x"
    return None

def run_free_convo_routine(win, win_master, photo_rect_on, photo_rect_off,
                           req_master, pub_master, pub_slave,
                           convo_countdown, convo_len, routineTimer):
    """
    Free conversation routine.

    Args:
        win (Window): Presentation window - win_main.
        win_master (Window): Researcher window at Master Pc.
        photo_rect_on (visual.Rect): Photodiode onset marker.
        photo_rect_off (visual.Rect): Photodiode offset marker.
        req_master (zmq.Socket): REQ socket for Master PC PupilCapture instance.
        pub_master (zmq.Socket): PUB socket for Master PC PupilCapture instance.
        pub_slave (zmq.Socket): REQ socket for Slave PC PupilCapture instance.
        convo_countdown (int): Countdown duration prior to conversation.
        convo_len (int): Conversation duration.
        routineTimer (psychopy.core.Clock): Local routine timer.
    """
    # marker - countdown starting
    comms.send_annotation(pub_master, pub_slave, f"start_countdown_free", req_master)

    # timer prep
    routineTimer.reset()
    frameN = -1
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")


    # stage 0: countdown
    countdown_text = visual.TextStim(win_master, text="", height=0.1, color='white', pos=(0, 0))
    wait_timer = core.Clock()
    response = _show_countdown(convo_countdown, win_master, wait_timer, countdown_text, "Countdown. Time left:")
    if response == "x":
        return

    # stage 1: photodiode comms and audio signal
    photo_toggle_time = 1
    toggle_cnt = 0
    max_toggles = 4
    photo_is_on = False
    last_toggle_time = 0

    routineTimer.reset()
    continueRoutine = True
    while continueRoutine:
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        frameN += 1

        if toggle_cnt < max_toggles and t >= last_toggle_time + photo_toggle_time:
            last_toggle_time = t
            if not photo_is_on:
                photo_rect_on.setAutoDraw(True)
                photo_rect_off.setAutoDraw(False)
            else:
                photo_rect_on.setAutoDraw(False)
                photo_rect_off.setAutoDraw(True)
            photo_is_on = not photo_is_on
            toggle_cnt += 1

        if toggle_cnt >= max_toggles:
            continueRoutine = False

        win.flip()

    photo_rect_on.setAutoDraw(False)
    photo_rect_off.setAutoDraw(True)

    # marker - conversation start
    comms.send_annotation(pub_master, pub_slave, "start_free_convo", req_master)
    # audio signal
    beep = sound.Sound("C", secs=1.0, stereo=True)
    beep.play()

    # stage 2: free conversation
    wait_timer = core.Clock()
    response = _show_countdown(convo_len, win_master, wait_timer, countdown_text, 'Free conversation. Time left:')
    if response == "x":
        pass

    # stage 3: photodiode comms and audio signal
    beep = sound.Sound("C", secs=1.0, stereo=True)
    beep.play()
    # marker - conversation finished
    comms.send_annotation(pub_master, pub_slave, "stop_free_convo", req_master)

    routineTimer.reset()
    toggle_cnt = 0
    last_toggle_time = 0
    photo_is_on = False
    continueRoutine = True
    while continueRoutine:
        t = routineTimer.getTime()
        frameN += 1

        if toggle_cnt < max_toggles and t >= last_toggle_time + photo_toggle_time:
            last_toggle_time = t
            if not photo_is_on:
                photo_rect_on.setAutoDraw(True)
                photo_rect_off.setAutoDraw(False)
            else:
                photo_rect_on.setAutoDraw(False)
                photo_rect_off.setAutoDraw(True)
            photo_is_on = not photo_is_on
            toggle_cnt += 1

        if toggle_cnt >= max_toggles:
            continueRoutine = False

        win.flip()

    photo_rect_on.setAutoDraw(False)
    photo_rect_off.setAutoDraw(True)
    routineTimer.reset()
