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