import site_obj

class SiteManager:
    def __init__(self):
        self.sites_obj = {}
        self.active_sites = {}
        self.all_var_last_commit_time = {}

    def create_all_sites(self):
        '''
            This function initializes 10 sites and updates site_manager object with site objects.
                self : site_manager object
        '''
        for i in range(1,11):
            new_site = site_obj.Site(i)
            self.sites_obj[i] = new_site
            self.active_sites[i] = True
    
    def choose_site(self, vname, operation):
        '''
            This function returns a chosen site based on variable selected.
        '''
        if (vname&1)==0:
            for i in range(1,11):
                if self.active_sites[i]:
                    if operation=="W":
                        return i
                    else:
                        if self.all_var_last_commit_time[vname] > self.sites_obj[i].last_down_time:
                            return i
        else:
            site_num = (1 + vname) % 10
            if self.active_sites[site_num]:
                return site_num
        return 0

    def read_variable(self, vname, tid):
        # choose site and return read value
        return 0

    def write_variable(self, vname, tid, value):
        # choose and write on site
        return 0

    def fail_site(self, site_id):
        # Update status of failed site and also note the fail time
        return False

    def recover_site(self, site_id):
        # Update status of recovered site and also note the recovery time
        return False