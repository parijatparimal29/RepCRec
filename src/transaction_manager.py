from data_manager import DataManager
from site_manager import SiteManager
import transaction
from queue import Queue

class TransactionManager:
    def __init__(self):
        self.all_transactions = {}
        self.waits_for = {}
        self.wait_queue = []
        self.instruction_queue = Queue()
        self.dependent_transactions = {}
        self.last_transaction_id_on_commit = None

    def detect_deadlocks(self):
        visited = set()
        terminal_ids = set()
        stack = []
        for t_id in self.waits_for:
            if t_id not in visited:
                stack.append(t_id)
                currentCycle = set()
                while stack:
                    curr_tid = stack.pop()
                    visited.add(curr_tid)
                    currentCycle.add(curr_tid)
                    wait_for_ids = self.waits_for[curr_tid]
                    is_terminal = True

                    for wait_tid in wait_for_ids:
                        if wait_tid in self.waits_for:
                            if wait_tid in visited and wait_tid not in terminal_ids:
                                return currentCycle.difference(terminal_ids)
                            stack.append(wait_tid)
                            is_terminal = False
                    if is_terminal:
                        terminal_ids.add(curr_tid)

        return False

    def resolve_deadlocks(self, sm, cycle):
        transactions = [self.all_transactions[tid] for tid in cycle]
        transactions.sort(key=lambda x: x.start_time)

        youngest_transaction = transactions.pop()
        if not youngest_transaction.to_abort:
            print("T{} aborts".format(youngest_transaction.tid))
        youngest_transaction.to_abort = True
        sm.clear_locks(youngest_transaction.tid, self.all_transactions[youngest_transaction.tid].variables_affected)
        self.update_wait_queue(youngest_transaction.tid)
        self.update_instruction_queue(youngest_transaction.tid)

    def get_next_instruction(self):
        if self.last_transaction_id_on_commit is not None:
            self.update_instruction_queue()
            self.last_transaction_id_on_commit = None

        if self.instruction_queue.empty():
            return None
        return self.instruction_queue.get()

    def update_instruction_queue(self, completed_tid = None):
        if completed_tid is None:
            completed_tid = self.last_transaction_id_on_commit
        blocked_tids = self.dependent_transactions.pop(completed_tid, set())
        if blocked_tids:
            # blocked_tids = sorted(list(blocked_tids))
            temp_queue = Queue()
            for instr in self.wait_queue:
                temp_queue.put(instr)
            self.wait_queue = []
            self.waits_for = {}
            self.dependent_transactions = {}
            while not self.instruction_queue.empty():
                temp_queue.put(self.instruction_queue.get())
            self.instruction_queue = temp_queue

    def add_instruction(self, instr):
        self.instruction_queue.put(instr)

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

    def decipher_locked_by(self, locked_by_str):
        tids = locked_by_str.split('[')[1].split(']')[0].split(", ")
        locked_by_list = list(map(int, tids))
        return locked_by_list

    def is_available_to_read(self, sm:SiteManager, vname):
        site_nums = [1 + (vname % 10)]
        if (vname&1)==0:
            site_nums = range(1,11)
        for site_num in site_nums:
            if sm.active_sites[site_num]:
                return True
        return False

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
            self.dump(sm)
        elif t_type == "B":
            if "RO" in instr:
                self.create_transaction(sm, tid, tick, True)
            else:
                self.create_transaction(sm, tid, tick, False)
        elif t_type == "E":
            self.commit_transaction(tid, sm)
            self.last_transaction_id_on_commit = tid
        elif t_type == "F":
            affected_tids = sm.fail_site(tid, tick)
            for affected_tid in affected_tids:
                self.abort_transaction(affected_tid)
        elif t_type == "RC":
            sm.recover_site(tid, tick)
        elif t_type == "R":
            if self.all_transactions[tid].is_RO:
                if vname in self.all_transactions[tid].RO_variables:
                    if self.is_available_to_read(sm, vname):
                        read_val = self.all_transactions[tid].RO_variables[vname]
                        print("x{}: {}".format(vname, read_val))
                    else:
                        self.abort_transaction(tid)
                else:
                    self.abort_transaction(tid)
                    print("Data does not exist. Aborting Transaction {}".format(tid))
            elif vname in self.all_transactions[tid].uncommitted_writes and self.all_transactions[tid].uncommitted_writes[vname][1] > sm.all_var_last_commit_time[vname]:
                read_val = self.all_transactions[tid].uncommitted_writes[vname][0]
                print("x{}: {}".format(vname, read_val))
            else:
                read_val = sm.read_variable(vname, tid)
                if read_val == "ABORT":
                    if not self.all_transactions[tid].to_abort:
                        self.abort_transaction(tid)
                elif "WAIT_S" in read_val:
                    print("Waiting for Site {} to recover".format(read_val.split('S')[1]))
                elif "WAIT" in read_val:
                    locked_by_list = self.decipher_locked_by(read_val.split('_')[1])
                    for locked_by in locked_by_list:
                        self.waits_for[tid] = self.waits_for.get(tid, set()).union([locked_by])
                        self.dependent_transactions[locked_by] = self.dependent_transactions.get(locked_by, set()).union([tid])
                        self.wait_queue.append(instr)
                        if not self.all_transactions[tid].to_abort:
                            print("T{} waiting for T{} to finish".format(tid, locked_by))
                else:
                    self.all_transactions[tid].variables_affected.add(vname)
                    print("x{}: {}".format(vname, read_val))
        elif t_type == "W":
            write_status = sm.write_variable(vname, tid)
            if write_status == "ABORT":
                if not self.all_transactions[tid].to_abort:
                    self.abort_transaction(tid)
            elif "WAIT" in write_status:
                locked_by_list = self.decipher_locked_by(write_status.split('_')[1])
                for locked_by in locked_by_list:
                    self.waits_for[tid] = self.waits_for.get(tid, set()).union([locked_by])
                    self.dependent_transactions[locked_by] = self.dependent_transactions.get(locked_by, set()).union([tid])
                    self.wait_queue.append(instr)
                    if not self.all_transactions[tid].to_abort:
                        print("T{} waiting for T{} to finish".format(tid, locked_by))
            else:
                self.all_transactions[tid].variables_affected.add(vname)
                self.all_transactions[tid].uncommitted_writes[vname] = [val, tick]
                print("Write to sites ->{} => x{}: {}".format(write_status, vname, val))

    def abort_transaction(self, tid):
        '''
        This function updates flag for transaction to abort when end instead of commit.
        Input:
            self  : TransactionManager object.
            tid   : tid of transaction
        '''
        print("T{} aborts".format(tid))
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
        message = "T{} aborted at commit time".format(tid)
        if not self.all_transactions[tid].to_abort:
            sm.commit_values(self.all_transactions[tid].uncommitted_writes)
            message = "T{} commits".format(tid)
        sm.clear_locks(tid, self.all_transactions[tid].variables_affected)
        print(message)

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

    def query_state(self, sm):
        # Print state of TM & SM
        print("Site Manager Details:")
        for i in range(1,11):
            self.print_site_details(sm.data_managers[i])
            print()
        print("Transaction Manager Details:")
        print("Transactions:")
        print("ID  Start Time  Abort  Read Only  RO Variables  Variables Affected  Uncommitted Writes")
        for tid,transaction in self.all_transactions.items():
            print(tid,"\t",transaction.start_time,"\t",transaction.to_abort,"\t",
                transaction.is_RO,"\t",transaction.RO_variables,"\t\t",
                transaction.variables_affected,"\t",transaction.uncommitted_writes)
        print("Wait-for:",self.waits_for)
        print("Wait-Queue:",self.wait_queue)

        return False

    def update_wait_queue(self, tid):
        self.waits_for.pop(tid, None)
        for t_id in self.waits_for:
            self.waits_for[t_id].discard(tid)
