class lock:
    def __init__(self, l_type, l_vname, l_tid, l_time):
        self.lock_type = l_type
        self.lock_vname = l_vname
        self.lock_tid = l_tid
        self.lock_time = l_time