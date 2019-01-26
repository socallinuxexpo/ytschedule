#!/usr/bin/env python
import logging
import time
import os
import daemon
from daemon import runner

rundir = os.path.join(os.path.dirname(__file__), '../run')
# print rundir
#


class Ytschedule():
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path = os.path.join(rundir, 'testdaemon.pid')
        self.pidfile_timeout = 5
        logger = logging.getLogger("DaemonLog")
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler = logging.FileHandler(os.path.join(rundir, "testdaemon.log"))
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    def run(self):
        while True:
            # Main code goes here ...
            # Note that logger level needs to be set to logging.DEBUG before this shows up in the logs
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warn("Warning message")
            logger.error("Error message")
            time.sleep(10)


app = Ytschedule()

daemon_runner = DaemonRunner(app)
# This ensures that the logger file handle does not get closed during daemonization
daemon_runner.daemon_context.files_preserve = [handler.stream]
daemon_runner.do_action()
