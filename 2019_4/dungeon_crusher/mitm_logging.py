import traceback
from mitmproxy import http
from mitmproxy import ctx


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def log_error(object_to_be_logged):
    if "do not know" != traceback.format_stack():
        print(f"{bcolors.FAIL}  {str(object_to_be_logged)}  {bcolors.ENDC}")
    # trace = traceback.format_stack()
    # if "mitmdump" in str(trace):

    #     ctx.log.error(str(object_to_be_logged))
    # else:
    #     print(object_to_be_logged)


def log_warning(object_to_be_logged):
    if "do not know" != traceback.format_stack():
        print(f"{bcolors.WARNING}  {str(object_to_be_logged)}  {bcolors.ENDC}")
    # trace = traceback.format_stack()
    # if "mitmdump" in str(trace):
    #     ctx.log.warn(str(object_to_be_logged))
    # else:
    #     print(object_to_be_logged)
