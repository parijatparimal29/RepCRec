class Transaction:
    def __init__(self, id, tick, is_RO):
        self.tid = id
        self.uncommitted_writes = {}
        self.start_time = tick
        self.is_RO = is_RO
        self.RO_variables = {}
        self.variables_affected = set()
        self.to_abort = False

