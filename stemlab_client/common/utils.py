import sys
import signal

def hasitems(collection):
    '''
    Test whether collection contains items or not.
    :param collection: list or dict to test for items
    :return: True if collection contains items, False if it doesn't
    '''
    if collection is not None and len(collection) > 0:
        return True
    else:
        return False

def generate_measurement_params(template, reading):
    post_dict = {}
    params = {}
    post_dict['href'] = template['href']
    for param_name in template['param_names']:
        params[param_name] = getattr(reading, param_name)
    post_dict['params'] = params
    return post_dict


class GracefulExit(object):
    exit_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.graceful_exit)
        signal.signal(signal.SIGTERM, self.graceful_exit)

    def graceful_exit(self, signum, frame):

        self.exit_now = True

