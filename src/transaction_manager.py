from data_manager import DataManager
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

    def decipher_instruction(self, instr):
        '''
        This function deciphers the instruction to return actionable information.
        Returns operation_type, transaction_id, variable_name, value as required by the instruction.
        Input:
            self  : TransactionManager object.
            instr : instruction to be deciphered for processing.
        '''
        if "dump" in instr:
            return "D", 0, 0, 0
        elif "begin" in instr:
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

    def process_instruction(self, sm:SiteManager, instr, tick):
        '''
        Processes each instruction by interaction of TM & SM.
        Input:
            self  : TransactionManager object.
            sm    : SiteManager object.
            instr : instruction to be processed.
            tick  : current time / tick - when the transaction is being executed.
        '''
        t_type, tid, vname, val = self.decipher_instruction(instr)

        # Prints deciphered instruction.
        #print("t_type: ", t_type, type(t_type),end='')
        #print("tid:    ", tid, type(tid),end='')
        #print("vname:  ", vname, type(vname),end='')
        #print("val:    ", val, type(val))

        if t_type == "D":
            self.dump()
        elif t_type == "B":
            if "RO" in instr:
                self.create_transaction(sm, tid, tick, True)
            else:
                self.create_transaction(sm, tid, tick, False)
        elif t_type == "E":
            self.commit_transaction(tid, sm)
        elif t_type == "F":
            sm.fail_site(tid, tick)
        elif t_type == "RC":
            sm.recover_site(tid, tick)
        elif t_type == "R":
            if self.all_transactions[tid].is_RO:
                if vname in self.all_transactions[tid].RO_variables:
                    read_val = self.all_transactions[tid].RO_variables[vname]
                else:
                    read_val = int(vname) * 10
                    print("x{}: {}".format(vname, read_val))
            elif vname in self.all_transactions[tid].uncommitted_writes and self.all_transactions[tid].uncommitted_writes[vname][1] > sm.all_var_last_commit_time[vname]:
                read_val = self.all_transactions[tid].uncommitted_writes[vname][0]
                print("x{}: {}".format(vname, read_val))
            else:
                read_val = sm.read_variable(vname, tid)
                if read_val == "ABORT":
                    self.abort_transaction(tid)
                elif "WAIT" in read_val:
                    locked_by = int(read_val.split('_')[1])
                    self.waits_for[locked_by] = tid
                    self.wait_queue[tid] = instr
                    print("T{} waiting for T{} to finish".format(tid, locked_by))
                else:
                    self.all_transactions[tid].variables_affected.add(vname)
                    print("x{}: {}".format(vname, read_val))
        elif t_type == "W":
            write_status = sm.write_variable(vname, tid)
            if write_status == "ABORT":
                self.abort_transaction(tid)
            elif "WAIT" in write_status:
                locked_by = int(write_status.split('_')[1])
                self.waits_for[locked_by] = tid
                self.wait_queue[tid] = instr
                print("T{} waiting for T{} to finish".format(tid, locked_by))
            else:
                self.all_transactions[tid].variables_affected.add(vname)
                self.all_transactions[tid].uncommitted_writes[vname] = val
                print("Write to sites ->{} => x{}: {}".format(write_status, vname, val))

    def abort_transaction(self, tid):
        '''
        This function updates flag for transaction to abort when end instead of commit.
        Input:
            self  : TransactionManager object.
            tid   : tid of transaction
        '''
        self.all_transactions[tid].to_abort = True

    def create_transaction(self, sm:SiteManager, tid, tick, is_RO):
        '''
            This function creates new transactions.
            Input:
                self  : TransactionManager object.
                sm    : SiteManager object.
                tid   : tid of transaction
                tick  : current tick
                is_RO : type of instruction. RO or Regular
        '''
        new_transaction = transaction.Transaction(tid, tick, is_RO)
        if is_RO:
            for i in range(1,21):
                 ro_val = sm.get_read_only_val(i)
                 if ro_val != -1:
                    new_transaction.RO_variables[i] = ro_val
        self.all_transactions[tid] = new_transaction
        print("Transaction T{} created at {}".format(tid, tick))

    def commit_transaction(self, tid, sm:SiteManager):
        '''
        This function either commits values or abort based on flag on Transaction.
        Input:
            self  : TransactionManager object.
            tid   : tid of transaction
            sm    : SiteManager object.
        '''
        if self.all_transactions[tid].to_abort:
            sm.clear_locks(tid, self.all_transactions[tid].variables_affected)
            print("Transaction {} aborted.".format(tid))
        else:
            sm.commit_values(self.all_transactions[tid].uncommitted_writes)
            sm.clear_locks(tid, self.all_transactions[tid].variables_affected)
            print("Transaction {} committed.".format(tid))

    def print_site_details(self, dm):
        '''
        Prints value of each variable at the given site / data manager.
        Input:
            self : TransactionManager object.
            dm   : DataManager object.
        '''
        print("site {} -".format(dm.site_id),end='')
        first = True
        for var in dm.variables:
            val = dm.variables[var]
            if first:
                print(" x{}: {}".format(var,val),end='')
                first = False
            else:
                print(", x{}: {}".format(var,val),end='')

    def dump(self, sm):
        '''
        Prints values of all variables present in sites / data_managers.
        Input:
            self : TransactionManager object
            sm   : SiteManager object.
        '''
        for i in range(1,11):
            self.print_site_details(sm.data_managers[i])
            print()

    def query_state(self, state_manager):
        # Print state of TM & SM
        return False