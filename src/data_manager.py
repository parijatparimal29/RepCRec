import lock

class DataManager:
    def __init__(self, id):
        self.site_id = id
        self.variables = {}
        self.site_active = True
        self.read_lock_table = {}
        self.write_lock_table = {}
        self.version_history = {}
        self.last_down_time = 0
        self.last_recovery_time = 0