import transaction

class transaction_manager:
    def __init__(self):
        self.all_transactions = {}
        self.waits_for = {}
        self.wait_queue = {}

    def detect_deadlocks(self, waits_for_graph):
        # Detect deadlock
        return False

    def decipher_instruction(self, instr):
        # Decipher instruction
        return instr, "RO"

    def process_instruction(self, site_manager, line):
        # Using site manager object, process instruction
        instr, t_type = self.decipher_instruction(line)
        return ""

    def execute_instruction(self, site_manger, instr, t_type):
        return False

    def abort_transaction(self, tid):
        # Abort transaction
        return False

    def create_transaction(self, tid):
        # Create transaction
        return False

    def commit_transaction(self, tid, site_manager):
        # Save uncommitted changes into sites
        return False

    def dump(self, site_manager):
        # Print status of variables in all sites
        return False

    def query_state(self, state_manager):
        # Print state of TM & SM
        return False