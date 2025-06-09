from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)
from psychopy import visual, core, event, sound
import msgpack as serializer
import comms

"""
These functions are mostly based on common code segments used in PsychoPy
They mostly serve to handle PsychoPy stimuli, windows and routine loops.
"""

# TODO: Proper argument and return types docstring

def setup_routine_components(components):
    """
    Initialize routine components.
    """
    for comp in components:
        comp.tStart = None
        comp.tStop = None
        comp.tStartRefresh = None
        comp.tStopRefresh = None
        if hasattr(comp, 'status'):
            comp.status = NOT_STARTED

def run_routine(win, routine_components, routine_timer, defaultKeyboard, msg='Running routine...', duration=None, escape_key="escape"):
    # TODO: duration is not safe, without specyfing it the code crashes
    """
    Using specific window 'win' (psychopy.visual.Window), creates routine segment with routine_componentes (list of PsychoPy stimuli) and runs it.
      routine_timer - (psychopy.core.Clock) Internal PsychoPy Clock
      defaultKeyboard - (psychopy.keyboard.Keyboard) Keyboard used for User interface.
      msg - (str) Message printed when run.
      duration - (int|None) How long routine will be run 
      escape_key - (str) String representation of the key which can be used to leave the routine. 
    """
    print(msg)

    frameTolerance = 0.005
    continue_routine = True
    t = 0
    frameN = -1
    routine_timer.reset()
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")

    while continue_routine:
        # Get current time
        t = routine_timer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routine_timer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN += 1

        # Update/draw components
        for comp in routine_components:
            if comp.status == NOT_STARTED and tThisFlip >= 0.0 - frameTolerance:
                comp.frameNStart = frameN
                comp.tStart = t
                comp.tStartRefresh = tThisFlipGlobal
                win.timeOnFlip(comp, 'tStartRefresh')
                comp.setAutoDraw(True)

            if comp.status == STARTED and duration and tThisFlipGlobal > comp.tStartRefresh + duration - frameTolerance:
                comp.tStop = t
                comp.frameNStop = frameN
                comp.setAutoDraw(False)

        # Check for quit
        if defaultKeyboard.getKeys(keyList=[escape_key]):
            core.quit()

        # Check if all components are finished
        continue_routine = any(
            hasattr(comp, "status") and comp.status == STARTED for comp in routine_components
        )

        # Refresh the screen
        if continue_routine:
            win.flip()

    # End routine: stop components
    for comp in routine_components:
        if hasattr(comp, "setAutoDraw"):
            comp.setAutoDraw(False)

def interrupt(msg, win, keys=('x',)):
    '''
    Prints msg (str) at win (psychopy.visual.Window) and waits for the User to press on of the keys (tuple)
    '''
    print(msg)
    message = visual.TextStim(win, text=msg, color='white')
    message.draw()
    win.flip()
    _ = event.waitKeys(keyList=keys)
    win.flip()

def run_calibration(req_port, sub_port, debug_mode=False):
    # TODO: Moze by tak upewniac sie ze kamery obu oczy sa wlaczone? wlasnie stracilismy na tym 5 min
    '''
    Runs calibration at specific PC, based on chosen req_port and sub_port (Context.socket).
    Evaluates whether the calibration quality is satisfactory and gives the User a choice to accept the quality
    or redo the calibration.
    debug_mode = True -> there is only a dummy calibration
    '''
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
    Using specific window 'win' (psychopy.visual.Window), creates routine segment with predefined stimuli: movies, photodiode marker and fixation cross.
      routineTimer - (psychopy.core.Clock) Internal PsychoPy Clock
      defaultKeyboard - (psychopy.keyboard.Keyboard) Keyboard used for User interface.
      msg - (str) Message printed when run.
      movie_duration - (int|None) How long routine will be run 
      thisExp - (dict) PsychoPy log dictionary.
    """
                           
    frameTolerance = 0.005 #0.005
    continueRoutine = True
    t = 0
    frameN = -1
    routineTimer.reset()
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    if movie_duration is None:
        movie_duration = movie.duration

    # Photodiode setup
    photo_rect_duration = movie_duration
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
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame

        if movie.status == NOT_STARTED and tThisFlip >= 0.0 - frameTolerance:
            # keep track of start time/frame for later
            movie.frameNStart = frameN  # exact frame index
            movie.tStart = t  # local t and not account for scr refresh
            movie.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(movie, 'tStartRefresh')  # time at next scr refresh
            # add timestamp to datafile
            thisExp.timestampOnFlip(win, '{}.started'.format(mov_name))
            movie.setAutoDraw(True)
        if movie.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > movie.tStartRefresh + movie_duration - frameTolerance:
                # keep track of stop time/frame for later
                movie.tStop = t  # not accounting for scr refresh
                movie.frameNStop = frameN  # exact frame index
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, '{}.stopped'.format(mov_name))
                movie.setAutoDraw(False)

        # Alternating the visual stimuli
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

        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()

        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in [movie]:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished

        # refresh the screen
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


def run_free_convo_routine(win, win_master, photo_rect_on, photo_rect_off,
                           req_master, pub_master, pub_slave,
                           convo_countdown, convo_len, routineTimer, thisExp, defaultKeyboard):

    noet = False
    if req_master is None or pub_master is None or pub_slave is None:
        noet = True

    if not noet:
        comms.send_annotation(pub_master, pub_slave, f"start_countdown_free", req_master)

    routineTimer.reset()
    frameN = -1
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")

    # Tekst countdownu na win_master
    countdown_text = visual.TextStim(win_master, text="", height=0.1, color='white', pos=(0, 0))

    # --- FAZA 0: Odczekanie 30 sekund z countdownem ---
    wait_timer = core.Clock()
    response = show_countdown(convo_countdown, win_master, wait_timer, countdown_text, "Rozbieg. Pozostało:")
    if response == "x":
        return

    # --- FAZA 1: Miganie fotodiody + dźwięk ---
    photo_toggle_time = 1  # sekundy
    toggle_cnt = 0
    max_toggles = 4  # 2 pelne migniecia (on/off)
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

    if not noet:
        comms.send_annotation(pub_master, pub_slave, "start_free_convo", req_master)
    beep = sound.Sound("C", secs=1.0, stereo=True)
    beep.play()

    # --- FAZA 2: 3 minuty swobodnej rozmowy ---
    wait_timer = core.Clock()
    response = show_countdown(convo_len, win_master, wait_timer, countdown_text, 'Swobodna rozmowa. Pozostało:')
    if response == "x":
        pass  # Przerywa 3 minuty wcześniej

    # --- FAZA 3: Miganie fotodiody + dźwięk ---
    beep = sound.Sound("C", secs=1.0, stereo=True)
    beep.play()
    if not noet:
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

def show_countdown(duration, win, timer, text_stim, text_content, key_list=["escape"]):
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