from subprocess import PIPE, Popen


class WindowCtrlError(Exception):

    pass


def focus_program(name):
    program_pids = _get_program_pids(name)
    if not program_pids:
        raise WindowCtrlError(f'{name} is not running')
    window_id = _get_window_id(program_pids)
    if window_id:
        _focus_window(window_id)
    else:
        raise WindowCtrlError(
            f'Unable to find {name} process, '
            'make sure you have wmctrl installed'
        )

def _get_program_pids(name):
    command = ['pgrep', name]
    with Popen(command, stdout=PIPE, stderr=PIPE) as proc:
        output, error = proc.communicate()
        return output.decode().split('\n')
    return []


def _get_window_id(pids):
    command = [
        'wmctrl',
        '-l',  # list windows
        '-p',  # show pids
    ]
    with Popen(command, stdout=PIPE, stderr=PIPE) as proc:
        output, error = proc.communicate()
        windows = (
            window
            for window in output.decode().split('\n')
            if window
        )
        for window in windows:
            window_id, workspace, pid, *_ = window.split()
            if pid in pids:
                return window_id
    return None


def _focus_window(window_id):
    command = [
        'wmctrl',
        '-i',  # search by id
        '-a',  # search
        window_id,
    ]
    with Popen(command, stderr=PIPE) as proc:
        output, error = proc.communicate()
