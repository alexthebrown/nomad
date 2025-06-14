from threading import Lock

class NomadControl:
    def __init__(self):
        self.command = None
        self.log = []
        self.lock = Lock()

    def add_log(self, entry):
        with self.lock:
            self.log.append(entry)
            if len(self.log) > 100:
                self.log.pop(0)

    def get_logs(self):
        with self.lock:
            return list(self.log)

    def set_command(self, cmd):
        with self.lock:
            self.command = cmd

    def consume_command(self):
        with self.lock:
            cmd = self.command
            self.command = None
            return cmd

nomad_control = NomadControl()
