import lock

class DataManager:
    def __init__(self, id):
        self.site_id = id
        self.variables = {}
        self.is_active = True
        self.is_recovering = False
        self.lock_table = {}
        self.last_down_time = 0
        self.last_recovery_time = 0