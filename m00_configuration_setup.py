

def create_session_name(expinfo:dict):
    ses_date, ses_time = expinfo['date'][:-7].split('_')
    ses_date = ses_date.replace('-', '_')
    ses_time = ses_time.replace('h', '')
    ses_pupil_file = f"{ses_date}_et_{ses_time}_{expinfo['participant']}"

    return ses_pupil_file