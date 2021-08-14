#! /usr/local/bin/python3
#
# groups v0.1
#
# Tony Williams 2021-08-09
#

"""See docstring for Groups class"""

import requests
from random import sample
import logging
import logging.handlers
import xml.etree.cElementTree as ET
from os import path
import plistlib

APPNAME = "groups"
LOGLEVEL = logging.DEBUG
LOGFILE = "/usr/local/var/log/%s.log" % APPNAME
SIZE = 10  # number of computers to add to group

__all__ = [APPNAME]


class Groups:
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
        self.url = prefs["JSS_URL"] + "/JSSResource/"
        self.auth = (prefs["API_USERNAME"], prefs["API_PASSWORD"])
        self.hdrs = {"accept": "application/json"}

    def get_computers(self):
        """get the list of computers"""
        r = requests.get(
            self.url + "computers", auth=self.auth, headers=self.hdrs
        )
        if r.status_code != 200:
            self.logger.error("Failed to get computers")
            self.logger.error(r.text)
            print("Failed to get computers")
            exit(1)
        self.computers = r.json()["computers"]

    def get_computer_groups(self):
        """get the computer groups"""
        url = self.url + "computer_groups"
        response = requests.get(url, auth=self.auth, headers=self.hdrs)
        if response.status_code != 200:
            self.logger.error("Failed to get computer groups")
            self.logger.error(response.text)
            print("Failed to get computer groups")
            exit(1)
        self.computer_groups = response.json()["computer_groups"]

    def random_computers(self):
        """get a random set of computers"""
        return sample(self.computers, SIZE)

    def one_group(self, group):
        """add computers to one group"""
        self.logger.info(f"Adding {SIZE} computers to {group['name']}")
        for computer in self.random_computers():
            ET.SubElement(group, "computers").append(
                self.add_one_computer(computer)
            )
        self.logger.info("Done")

    def add_one_computer(self, computer):
        """add one computer to a group"""
        url = self.url + f"computers/id/{computer['id']}"
        response = requests.get(url, auth=self.auth, headers=self.hdrs)
        if response.status_code != 200:
            self.logger.error("Failed to get computer")
            self.logger.error(response.text)
            print("Failed to get computer")
            exit(1)
        computer = response.json()["computer"]
        new = f"""
        <computer>
        <id>{id}</id>
        <name>{computer['general']['name']}</name>
        <mac_address>{computer['general']['mac_address']}</mac_address>
        <alt_mac_address>{computer['general']['alt_mac_address']}</alt_mac_address>
        <serial_number>{computer['general']['serial']}</serial_number>
        </computer>
        """
        new = "".join(new.split())
        return ET.fromstring(new)

    def main(self):
        """main"""
        self.setup_logging()
        self.load_prefs()
        self.computers = self.get_computers()
        self.get_computer_groups()
        self.logger.info("Adding computers to groups")
        for group in self.computer_groups:
            self.one_group(group)
            self.logger.info(f"Adding {SIZE} computers to {group['name']}")
        self.logger.info("Done")


if __name__ == "__main__":
    Groups().main()
