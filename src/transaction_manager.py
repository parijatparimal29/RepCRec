import transaction

class TransactionManager:
    def __init__(self):
        self.all_transactions = {}
        self.last_transaction_tid = 0
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
        # if instr is transaction related, process it.
        # if instr is read or write,
        # get operation as R or W and call function,
        # choose site from site manager based on vname & operation extracted from instr.
        # Perform required action through site manager
        return False

    def abort_transaction(self, tid):
        # Abort transaction
        return False

    def create_transaction(self, tick, type):
        '''
            This function creates new transactions.
            Input:
                tick: current tick
                type: type of instruction. RO or Regular
        '''
        tid = self.last_transaction_tid + 1
        new_transaction = transaction.Transaction(tid, tick, type)
        self.all_transactions[tid] = new_transaction
        self.last_transaction_tid = tid
        return tid

    def commit_transaction(self, tid, site_manager):
        # Save uncommitted changes into sites
        return False

    def dump(self, site_manager):
        # Print status of variables in all sites
        return False

    def query_state(self, state_manager):
        # Print state of TM & SM
        return False