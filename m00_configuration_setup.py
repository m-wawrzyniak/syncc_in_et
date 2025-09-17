"""
Contains functions used during configuration setup.
"""

from config import WIN_SIZES

def create_session_name(expinfo:dict):
    """
    Creates standardized recording session name, based on the date and participant ID.

    Args:
        expinfo (dict): PsychoPy-based dictionary with info concerning the experiment.

    Returns:
        ses_pupil_file (str): Session name, under which PupilCapture recordings will be saved.
    """
    ses_date, ses_time = expinfo['date'][:-7].split('_')
    ses_date = ses_date.replace('-', '_')
    ses_time = ses_time.replace('h', '')
    ses_pupil_file = f"{ses_date}_et_{ses_time}_{expinfo['participant']}"

    return ses_pupil_file

def check_screens_id(screens:list):
    """
    Checks whether screen IDs on Win OS have been assigned correctly, so that PsychoPy windows are opened on correct
    displays.

    Args:
        screens (list): List of screens, coming from pyglet.canvas.get_display().get_screens().

    """
    for i, screen in enumerate(screens):
        print(f"Screen {i}: {screen.width}x{screen.height}, x={screen.x}, y={screen.y}")
        if screen.width != WIN_SIZES[i][0] or screen.height != WIN_SIZES[i][1]:
            raise TypeError(
                f"Screen {i} resolution mismatch. Expected {WIN_SIZES[i]}, got {(screen.width, screen.height)} instead.")