import signal, sys, os, traceback

os.environ.setdefault("PROCESS_TITLE", "aiServer")

from time import sleep
from twisted.application import service

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from server import AiService
from commonlib.glog import glog


def start(application):
    try:
        aiService = AiService()
        aiService.startService(application, __name__)
    except Exception as error:
        glog.error(f"{type(error).__name__}: {error}")
        sys.exit()


def stop():
    try:
        aiService = AiService()
        if not aiService.isRunniing():
            return

        glog.info("stop server")

        aiService.stopService(__name__)

    except Exception as error:
        glog.error(f"{type(error).__name__}: {error}")
        glog.error("graceful shutdown failed")


# gracefull stop server
def gracefulShutdown(signum, frame):
    glog.info('captured signal {}'.format(signum))
    # traceback.print_stack(frame)

    stop()

    try:
        sys.exit()
    except SystemExit:  # this always raises SystemExit
        glog.info("sys.exit() worked as expected")
    except:  # some other exception got raised
        glog.error("Something went horribly wrong")


# register signal handlers
signal.signal(signal.SIGINT, gracefulShutdown)
signal.signal(signal.SIGTERM, gracefulShutdown)

if sys.platform != "win32":
    signal.signal(signal.SIGHUP, gracefulShutdown)
    signal.signal(signal.SIGQUIT, gracefulShutdown)

application = service.Application("Ai")


def main():
    start(application)


main()
