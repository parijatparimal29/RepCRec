class Lock:
    def __init__(self, l_tid, l_type):
        self.lock_type = l_type
        self.R_lock_tids = set()
        self.W_lock_tid = set()
        if l_type == "R":
            self.R_lock_tids.add(l_tid)
        else:
            self.W_lock_tid.add(l_tid)

    def have_lock(self, tid, l_type):
        if self.lock_type == "W":
            return tid in self.W_lock_tid
        elif l_type == "R" and self.lock_type=="R":
            return tid in self.R_lock_tids
        return False

    def add_lock(self, tid, l_type):
        if l_type == "R" and self.lock_type == "R":
            self.R_lock_tids.add(tid)
            return True
        elif l_type == "W" and self.lock_type == "R" and (len(self.R_lock_tids)==0 or (len(self.R_lock_tids) == 1 and tid in self.R_lock_tids)):
            self.lock_type = "W"
            self.R_lock_tids = set()
            self.W_lock_tid.add(tid)
            return True
        else:
            return False

    def release_lock(self, tid):
        if self.lock_type == "W" and tid in self.W_lock_tid:
            self.lock_type = "R"
            self.R_lock_tids = set()
            self.W_lock_tid = set()
        elif self.lock_type == "R" and tid in self.R_lock_tids:
            self.R_lock_tids.remove(tid)

    def get_locked_by(self, tid):
        if self.lock_type == "R":
            for l_tid in self.R_lock_tids:
                if l_tid != tid:
                    return l_tid
            return tid
        else:
            for l_tid in self.W_lock_tid:
                return l_tid



