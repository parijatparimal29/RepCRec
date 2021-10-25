class transaction:
    def __init__(id, tick, is_RO):
        tid = id
        current_instruction = ""
        uncommitted_writes = {}
        start_time = tick
        transaction_type = is_RO

