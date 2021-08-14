#! /usr/local/bin/python3
#
# users v0.1
#
# Tony Williams 2021-08-09
#

"""See docstring for Users class"""

import requests
import logging
import logging.handlers
from os import path
import plistlib
from re import search

APPNAME = "users"
LOGLEVEL = logging.DEBUG
LOGFILE = "/usr/local/var/log/%s.log" % APPNAME

__all__ = [APPNAME]


class Users:
    """
    Class to handle the users list. If you run `sanitise.py` first then the
    details of anyone who owns a computer will have been changed and their
    `name` will start with 'ID' followed by digits
    """

    def setup_logging(self):
        """Defines a nicely formatted logger"""

        self.logger = logging.getLogger(APPNAME)
        self.logger.setLevel(LOGLEVEL)
        # we may be the second and subsequent iterations of JPCImporter
        # and already have a handler.
        if len(self.logger.handlers) > 0:
            return
        handler = logging.handlers.TimedRotatingFileHandler(
            LOGFILE, when="D", interval=1, backupCount=7
        )
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        self.logger.addHandler(handler)

    def load_prefs(self):
        """ load the preferences from file """
        plist = path.expanduser(
            "~/Library/Preferences/com.github.nfr.autopkg.plist"
        )
        prefs = plistlib.load(open(plist, "rb"))
        self.url = prefs["JSS_URL"] + "/JSSResource/users"
        self.auth = (prefs["API_USERNAME"], prefs["API_PASSWORD"])
        self.hdrs = {"accept": "application/json"}

    def main(self):
        self.setup_logging()
        self.load_prefs()
        self.logger.info("Starting %s", APPNAME)
        response = requests.get(
            url=self.url, auth=self.auth, headers=self.hdrs
        )
        if response.status_code != 200:
            self.logger.error(
                "Error getting users from %s: %s", self.url, response.text
            )
            return
        for user in response.json()["users"]:
            print("Found %s" % user["name"])
            if search("U", user["name"]):
                self.logger.info("deleting %s", user["name"])
                response = requests.delete(
                    url=f"{self.url}/id/{user['id']}", auth=self.auth
                )
                print(f"Deleted: {user["name"]} Status: response.status_code")


if __name__ == "__main__":
    Users().main()
