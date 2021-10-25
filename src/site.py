import lock

class site:
    def __init__(id):
        site_id = id
        variables = {}
        site_active = True
        read_lock_table = {}
        write_lock_table = {}
        version_history = {}
        last_down_time = 0
        last_recovery_time = 0
