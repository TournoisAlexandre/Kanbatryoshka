import sys
import traceback
from kanbatryoshka.app import KanbatryoshkaApp

import sys, traceback

def global_excepthook(exc_type, exc_value, tb):
    print("=== UNCAUGHT EXCEPTION ===")
    traceback.print_exception(exc_type, exc_value, tb)
    sys.exit(1)

sys.excepthook = global_excepthook

from PySide6.QtCore import qInstallMessageHandler, QtMsgType

def qt_message_handler(mode, context, message):
    modes = {
        QtMsgType.QtDebugMsg:   "DEBUG",
        QtMsgType.QtInfoMsg:    "INFO",
        QtMsgType.QtWarningMsg: "WARNING",
        QtMsgType.QtCriticalMsg:"CRITICAL",
        QtMsgType.QtFatalMsg:   "FATAL",
    }
    print(f"[{modes.get(mode,'')}] {message}")

qInstallMessageHandler(qt_message_handler)

import faulthandler
import sys
import signal

faulthandler.enable(file=sys.stderr, all_threads=True)

def _dump_and_exit(sig, frame):
    sys.stderr.write(f"\n*** Caught signal {sig} ***\n")
    faulthandler.dump_traceback(file=sys.stderr, all_threads=True)
    sys.exit(1)

for s in (signal.SIGSEGV, signal.SIGABRT, getattr(signal, "SIGFPE", None)):
    if s is not None:
        try:
            signal.signal(s, _dump_and_exit)
        except (ValueError, OSError):
            pass


if __name__ == "__main__":
    app = KanbatryoshkaApp()
    exit_code = app.run()
    exit(exit_code)