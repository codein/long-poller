import sys
import gtk
import appindicator
import pprint
import imaplib
import requests

from config.creds import default

#TODO(codein) 
#TODO(codein) notify-send noification 
#TODO(codein) notofiction with hyperlink to pullrequest 
#TODO(codein) ubuntu refactor notification logic from polling logic  
#TODO(codein) input form for user name n pass 


PING_FREQUENCY = 10 # seconds
pull_requests = [{'repo':'vcd_extensions' , 'pull_request_number': 4}]


class Check:
    def __init__(self):
        self.ind = appindicator.Indicator("github-indicator",
                                           "",
                                           appindicator.CATEGORY_COMMUNICATIONS)
        self.ind.set_icon_theme_path("/home/codein/Desktop/icon")
        self.ind.set_icon("github_blue_white_cat_32")
        self.ind.set_status(appindicator.STATUS_ACTIVE)
        self.ind.set_attention_icon("github_white_black_cat_32")
        self.menu_setup()
        self.pull_requests = pull_requests
        self.last_updated_at_map = {}
        self.ind.set_menu(self.menu)

    def menu_setup(self):
        self.menu = gtk.Menu()

        self.quit_item = gtk.MenuItem("Quit")
        self.quit_item.connect("activate", self.quit)
        self.quit_item.show()
        self.menu.append(self.quit_item)

    def main(self):
        self.initialize_pulls()
        self.check_pulls()
        gtk.timeout_add(PING_FREQUENCY * 1000, self.check_pulls)
        gtk.main()

    def quit(self, widget):
        sys.exit(0)

    def initialize_pulls(self):
        for pull_request in self.pull_requests:
            repo = pull_request['repo']
            pull_request_number = pull_request['pull_request_number']
            lookup_key = '%s/pulls/%d' % (repo, pull_request_number)
            last_updated_at = self.get_last_updated_at(repo, pull_request_number)
            if last_updated_at:   
                print '%s not found' % lookup_key
                self.last_updated_at_map[lookup_key] = last_updated_at
                                        
    def check_pulls(self):
        for pull_request in self.pull_requests:
            repo = pull_request['repo']
            pull_request_number = pull_request['pull_request_number']        
            lookup_key = '%s/pulls/%d' % (repo, pull_request_number)
            last_updated_at = self.get_last_updated_at(repo, pull_request_number)
            if last_updated_at: 
                if lookup_key in self.last_updated_at_map:
                    if self.last_updated_at_map[lookup_key] < last_updated_at:
                        print '%s updated' % lookup_key
                        self.last_updated_at_map[lookup_key] = last_updated_at
                        self.ind.set_status(appindicator.STATUS_ATTENTION)
                    else:
                        print '%s no change' % lookup_key 
                        if self.ind.get_status() != appindicator.STATUS_ATTENTION:
                            self.ind.set_status(appindicator.STATUS_ACTIVE)                
                else:
                    print '%s not found' % lookup_key
                    self.last_updated_at_map[lookup_key] = last_updated_at
            return True

    def get_last_updated_at(self, repo, pull_request_number):
        url = 'https://api.github.com/repos/Navisite/%s/pulls/%d/comments' % (repo, pull_request_number)
        creds = default
        try:
            request = requests.get(url, auth=creds)
            if request.status_code == requests.codes.ok or request.status_code == requests.codes.created:
                success = True
                print pprint.pprint(request.json)
                last_updated_at = max([comment['updated_at'] for comment in request.json])
                print '%s updates %s' % (last_updated_at, url)
                return last_updated_at
            else:
                return False
        except requests.RequestException:
            return None

if __name__ == "__main__":
    indicator = Check()
    indicator.main()