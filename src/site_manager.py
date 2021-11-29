import data_manager

class SiteManager:
    def __init__(self):
        self.data_managers = {}
        self.active_sites = {}
        self.all_var_last_commit_time = {}

    def create_all_sites(self):
        '''
            This function initializes 10 sites and updates site_manager object with site objects.
                self : site_manager object
        '''
        for i in range(1,11):
            new_site = data_manager.DataManager(i)
            self.data_managers[i] = new_site
            self.active_sites[i] = True
    
    def choose_site(self, vname, operation):
        '''
            This function returns a chosen site based on variable selected.
            To do: check lock status at site and return site according to lock availability.
        '''
        if (vname&1)==0:
            for i in range(1,11):
                if self.active_sites[i]:
                    if self.all_var_last_commit_time[vname] > self.data_managers[i].last_down_time:
                        return i
        else:
            site_num = (1 + vname) % 10
            if self.active_sites[site_num]:
                return site_num
        return 0

    def get_locks(self, tid, vname, l_type):
        '''
        Checks if locks are available for the transaction to complete. 
        Creates / updates locks as required by transaction. 
        Returns True if lock acquired on all active sites with variable.
        Returns False if lock cannot be acquired.
        Input:
            self    : SiteManager Object.
            tid     : Transaction id of transaction that requires the locks.
            vname   : Variable name that needs to be locked.
            l_type  : Type of lock required - R (Read) or W (Write).
        '''
        found_lock = False
        if (vname&1)==0:
            for site_num in self.active_sites:
                if self.active_sites[site_num]:
                    this_site = self.data_managers[site_num]
                    if vname not in this_site.lock_table[vname]:
                        this_site.lock_table[vname] = (tid, l_type)
                        found_lock = True
                    elif this_site.lock_table[vname][0] == tid:
                        if this_site.lock_table[vname][1] != "W":
                            this_site.lock_table[vname][1] = l_type
                        found_lock = True
                    else:
                        return False
        else:
            site_num = (1 + vname) % 10
            if self.active_sites[site_num]:
                this_site = self.data_managers[site_num]
                if vname not in this_site.lock_table[vname]:
                    this_site.lock_table[vname] = (tid, l_type)
                    found_lock = True
                elif this_site.lock_table[vname][0] == tid:
                    if this_site.lock_table[vname][1] != "W":
                        this_site.lock_table[vname][1] = l_type
                    found_lock = True
                else:
                    return False
        return found_lock

    def read_variable(self, vname, tid, site_id):
        # choose site and return read value
        return False

    def write_variable(self, vname, tid, value, tick):
        # choose and write on site
        return 0

    def fail_site(self, site_id, tick):
        # Update status of failed site and also note the fail time
        return False

    def recover_site(self, site_id, tick):
        # Update status of recovered site and also note the recovery time
        return False