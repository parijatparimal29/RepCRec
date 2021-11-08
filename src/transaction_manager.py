from site_manager import SiteManager
import transaction

class TransactionManager:
    def __init__(self):
        self.all_transactions = {}
        self.waits_for = {}
        self.wait_queue = {}

    def detect_deadlocks(self):
        # Detect deadlock using waits_for adjacency matrix for transaction waiting graph
        return False

    def decipher_instruction(self, instr:str):
        # Decipher instruction
        if "begin" in instr:
            tid = int(instr.split('T')[1].split(')')[0])
            return "B", tid, 0, 0
        elif "end" in instr:
            tid = int(instr.split('T')[1].split(')')[0])
            return "E", tid, 0, 0
        elif "fail" in instr:
            dm = int(instr.split('(')[1].split(')')[0])
            return "F", dm, 0, 0
        elif "recover" in instr:
            dm = int(instr.split('(')[1].split(')')[0])
            return "RC", dm, 0, 0
        elif "R(" in instr:
            tid = int(instr.split('T')[1].split(',')[0])
            vname = int(instr.split('x')[1].split(')')[0])
            return "R", tid, vname, 0
        elif "W(" in instr:
            tid = int(instr.split('T')[1].split(',')[0])
            vname = int(instr.split('x')[1].split(',')[0])
            val = int(instr.split(',')[2].split(')')[0])
            return "W", tid, vname, val

    def process_instruction(self, sm:SiteManager, instr:str, tick:int):
        # Using site manager object, process instruction
        # Need to add check for aborted transactions
        t_type, tid, vname, val = self.decipher_instruction(instr)
        if t_type == "B":
            if "RO" in instr:
                self.create_transaction(tid, tick, True)
            else:
                self.create_transaction(tid, tick, False)
        elif t_type == "E":
            self.commit_transaction(tid, sm)
        elif t_type == "F":
            sm.fail_site(tid, tick)
        elif t_type == "RC":
            sm.recover_site(tid, tick)
        elif t_type == "R":
            dm = sm.choose_site(vname, "R")
            if dm == 0:
                self.abort_transaction(tid)
            elif dm < 0:
                self.waits_for[abs(dm)] = tid
                self.wait_queue[tid] = instr
            else:
                val = sm.read_variable(vname, tid, dm)
                print("x{}:{}".format(vname, val))
        elif t_type == "W":
            write_success = sm.write_variable(vname, tid, val, tick)
            if not write_success:
                self.abort_transaction(tid)

    def abort_transaction(self, tid):
        # Abort transaction
        return False

    def create_transaction(self, tid, tick, is_RO):
        '''
            This function creates new transactions.
            Input:
                tick: current tick
                type: type of instruction. RO or Regular
        '''
        new_transaction = transaction.Transaction(tid, tick, is_RO)
        self.all_transactions[tid] = new_transaction
        self.last_transaction_tid = tid

    def commit_transaction(self, tid, sm):
        # Save uncommitted changes into sites
        return False

    def dump(self, sm:SiteManager):
        # Print status of variables in all sites
        
        return False

    def query_state(self, state_manager):
        # Print state of TM & SM
        return False