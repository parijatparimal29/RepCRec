class Transaction:
    def __init__(self, id, tick, is_RO):
        self.tid = id
        self.current_instruction = ""
        self.uncommitted_writes = {}
        self.start_time = tick
        self.transaction_type = is_RO

