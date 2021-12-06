import data_manager
import lock

class SiteManager:
    def __init__(self):
        self.data_managers = {}
        self.active_sites = {}
        self.all_var_last_commit_time = {}

    def create_all_sites(self):
        '''
            This function initializes 10 sites and updates SiteManager object with site objects.
                self : SiteManager object
        '''
        for i in range(1,11):
            new_site = data_manager.DataManager(i)
            self.data_managers[i] = new_site
            self.active_sites[i] = True

    def choose_site(self, vname):
        '''
            This function returns a chosen site for read based on variable selected.
            If no sites are up that contains the variable data, 0 is returned.
            Returns site num that has the latest value of the variable.
            Input:
                self : SiteManager object
                vname  : Variable name that needs to be locked.
        '''
        site_nums = [1 + (vname % 10)]
        if (vname&1)==0:
            site_nums = range(1,11)
        for site_num in site_nums:
            if self.active_sites[site_num]:
                if self.data_managers[site_num].is_recovering:
                    if vname in self.all_var_last_commit_time and self.all_var_last_commit_time[vname] > self.data_managers[site_num].last_down_time:
                        return site_num
                else:
                    return site_num
        return 0

    def get_locks(self, tid, vname, l_type):
        '''
        Checks if locks are available for the transaction to complete.
        Creates / updates locks as required by transaction.
        Returns (True, tid) if lock acquired on all active sites with variable.
        Returns (False, locked_by) if lock cannot be acquired.
        Input:
            self   : SiteManager object
            tid    : Transaction id of transaction that requires the locks.
            vname  : Variable name that needs to be locked.
            l_type : Type of lock required - R (Read) or W (Write).
        '''
        found_lock = False
        site_nums = [1 + (vname % 10)]
        if (vname&1)==0:
            site_nums = self.active_sites
        for site_num in site_nums:
            if self.active_sites[site_num]:
                this_site = self.data_managers[site_num]
                if vname not in this_site.lock_table:
                    this_site.lock_table[vname] = lock.Lock(tid, l_type)
                    found_lock = True
                elif this_site.lock_table[vname].have_lock(tid, l_type) or this_site.lock_table[vname].add_lock(tid, l_type):
                    found_lock = True
                else:
                    if found_lock:
                        return (False, -1)
                    else:
                        return (False, this_site.lock_table[vname].get_locked_by(tid))
        return (found_lock, tid)

    def get_value_at_site(self, vname, site_num):
        '''
        Returns value of variable at specified site.
        Returns a default value if variable not initialized at site.
        Input:
            self     : SiteManager object.
            vname    : variable name that needs to be read.
            site_num : Site number of data manager to read from.
        '''
        if vname in self.data_managers[site_num].variables:
            return self.data_managers[site_num].variables[vname]
        else:
            return int(vname) * 10

    def read_variable(self, vname, tid):
        '''
        Gets locks, chooses site to read variable from.
        Reads the value of variable and returns it.
        If lock fails or site down, return appropriate message for Transaction Manager.
        Input:
            self  : SiteManager object.
            vname : variable name that needs to be read.
            tid   : Transaction id of transaction that requires the read operation.
        '''
        found_lock, locked_tid = self.get_locks(tid, vname, "R")
        if found_lock:
            site_num = self.choose_site(vname)
            if site_num==0:
                return "ABORT"
            else:
                return str(self.get_value_at_site(vname, site_num))
        else:
            if locked_tid==-1:
                return "ABORT"
            else:
                return "WAIT_"+str(locked_tid)

    def get_list_of_sites_to_write(self, vname):
        '''
        Fetches list of sites that will be affected by the write operation.
        Input:
            self  : SiteManager object.
            vname : variable name that needs to be written.
        '''
        list_active_sites = ""
        site_nums = [1 + (vname % 10)]
        if (vname&1)==0:
            site_nums = range(1,11)
        for site_num in site_nums:
            if self.active_sites[site_num]:
                list_active_sites += " "+str(site_num)
        return list_active_sites

    def write_variable(self, vname, tid):
        '''
        Gets write locks.
        If lock fails or site down, return appropriate message for Transaction Manager.
        Input:
            self  : SiteManager object.
            vname : variable name that needs to be written.
            tid   : Transaction id of transaction that requires the read operation.
        '''
        found_lock, locked_tid = self.get_locks(tid, vname, "W")
        if found_lock:
            return self.get_list_of_sites_to_write(vname)
        else:
            if locked_tid==-1:
                return "ABORT"
            else:
                return "WAIT_"+str(locked_tid)

    def fail_site(self, site_id, tick):
        '''
        This function updates status of data manager / site object.
        Also clears the lock_table for the site.
        Input:
            self    : SiteManager object.
            site_id : ID of site that has failed.
            tick    : Time at which site failed.
        '''
        self.active_sites[site_id] = False
        dm = self.data_managers[site_id]
        dm.is_active = False
        dm.lock_table = {}
        dm.last_down_time = tick

    def recover_site(self, site_id, tick):
        '''
        This function updates status of data manager / site object.
        Input:
            self    : SiteManager object.
            site_id : ID of site that has failed.
            tick    : Time at which site failed.
        '''
        self.active_sites[site_id] = True
        dm = self.data_managers[site_id]
        dm.is_active = True
        dm.is_recovering = True
        dm.last_recovery_time = tick

    def get_read_only_val(self, vname):
        '''
        This function fetches the last committed value of the variable from an active site.
        This read operation does not require two-phase locking, instead it follows multiversion read concurrency.
        Input:
            self  : SiteManager object.
            vname : variable name that needs to be read.
        '''
        site_nums = [1 + (vname % 10)]
        if (vname&1)==0:
            site_nums = range(1,11)
        for site_num in site_nums:
            returnData = False
            if self.active_sites[site_num]:
                if self.data_managers[site_num].is_recovering:
                    if vname in self.all_var_last_commit_time and self.all_var_last_commit_time[vname] > self.data_managers[site_num].last_down_time:
                        returnData = True
                else:
                    returnData = True

                if returnData:
                    if vname in self.data_managers[site_num].variables:
                        return self.data_managers[site_num].variables[vname]
        return -1

    def clear_locks(self, tid, affected_variables):
        '''
        This function clears locks held by the transaction.
        Used when either a transaction commits or aborts.
        Input:
            self               : SiteManager object.
            tid                : transaction id of transaction that commits or aborts.
            affected_variables : list of variables locked by transaction.
        '''
        for x in affected_variables:
            site_nums = [1 + (x % 10)]
            if (x&1)==0:
                site_nums = range(1,11)
            for site_num in site_nums:
                if self.active_sites[site_num] and x in self.data_managers[site_num].lock_table:
                    self.data_managers[site_num].lock_table[x].release_lock(tid)

    def commit_values(self, uncommitted_values):
        '''
        This function commits values in all active sites.
        Used when a transaction commits.
        Input:
            self               : SiteManager object.
            uncommitted_values : Values modified by transaction but not yet committed.
        '''
        for x in uncommitted_values:
            site_nums = [1 + (x % 10)]
            if (x&1)==0:
                site_nums = range(1,11)
            for site_num in site_nums:
                if self.active_sites[site_num]:
                    self.data_managers[site_num].variables[x] = uncommitted_values[x]
