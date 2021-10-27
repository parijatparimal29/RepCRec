import site

class site_manager:
    def __init__(self):
        self.sites = {}
        self.all_site_status = {}
        self.all_var_last_commit_time = {}

    def create_all_sites(self):
        # Create 10 site objects and store in sites dict.
        # Initialize site status for each site
        return False
    
    def choose_site(self, vname, operation):
        # choose site based on variable and operation required
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