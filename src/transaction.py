class Transaction:
    def __init__(self, id, tick, is_RO):
        self.tid = id
        self.current_instruction = ""
        self.uncommitted_writes = {}
        self.start_time = tick
        self.is_RO = is_RO
        self.RO_variables = {}

