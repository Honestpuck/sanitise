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


class Groups:
    """
    Class to modify Jamf Pro Cloud computer groups by adding random computers
    """

    def error(self, response, message):
        """ handle a requests error"""
        self.logger.error(message)
        self.logger.error(response.text)
        self.logger.error(response.status_code)
        self.logger.error(response.url)
        print(message)
        exit(1)

    def setup_logging(self):
        """Defines a nicely formatted logger"""
        self.logger = logging.getLogger(APPNAME)
        self.logger.setLevel(LOGLEVEL)
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
        self.hdrs = {"accept": "application/json"}

        # let's use the cookies to make sure we hit the
        # same server for every request.
        # The complication here is that ordinary and Premium Jamfers
        # get two DIFFERENT cookies for this.

        # the front page will give us the cookies
        r = requests.get(prefs["JSS_URL"])

        cookie_value = r.cookies.get("APBALANCEID")
        if cookie_value:
            # we are NOT premium Jamf Cloud
            self.cookies = dict(APBALANCEID=cookie_value)
        else:
            self.cookies = dict(AWSALB=r.cookies["AWSALB"])
        # now let's build a session
        self.sess = requests.Session()
        self.sess.cookies = self.cookies
        self.sess.auth = (prefs["API_USERNAME"], prefs["API_PASSWORD"])
        # we don't add the headers as we don't want JSON every time

    def get_computers(self):
        """get the list of computers"""
        response = sess.requests.get(self.url + "computers", headers=self.hdrs)
        if response.status_code != 200:
            self.error(response, "Could not get computer list")
        return response.json()["computers"]

    def get_computer_groups(self):
        """get the computer groups"""
        response = sess.requests.get(
            self.url + "computergroups", headers=self.hdrs
        )
        if response.status_code != 200:
            self.error(response, "Could not get computer groups")
        return response.json()["computer_groups"]

    def random_computers(self):
        """get a random set of computers"""
        a = []
        for n in sample(range(1, len(self.computers)), SIZE):
            a.append(self.computers[n])
        return a

    def one_group(self, group):
        """add computers to one group"""
        self.logger.info(f"Adding {SIZE} computers to {group['name']}")
        response = sess.requests.get(
            self.url + "computergroups/id/" + str(group["id"])
        )
        if response.status_code != 200:
            self.error(response, "Could not get computer group")
        grp = ET.fromstring(response.text)
        size = ET.fromstring("<size>10</size>")
        ET.SubElement(grp, "computers").append(size)
        for computer in self.random_computers():
            ET.SubElement(grp, "computers").append(
                self.add_one_computer(computer)
            )
        response = sess.requests.put(
            self.url + "computergroups/id/" + str(group["id"]),
            data=ET.tostring(grp, encoding="unicode"),
        )
        if response.status_code != 201:
            self.error(response, "Could not update computer group")
        self.logger.info(f"Finished {group['name']}")

    def add_one_computer(self, computer):
        """add one computer to a group"""
        response = sess.requests.get(
            self.url + f"computers/id/{str(computer['id'])}", headers=self.hdrs
        )
        if response.status_code != 200:
            self.error(response, "Could not get computer")
        computer = response.json()["computer"]
        new = f"""
        <computer>
        <id>{computer['general']['id']}</id>
        <name>{computer['general']['name']}</name>
        <mac_address>{computer['general']['mac_address']}</mac_address>
        <alt_mac_address>{computer['general']['alt_mac_address']}</alt_mac_address>
        <serial_number>{computer['general']['serial_number']}</serial_number>
        </computer>
        """
        new = "".join(new.split())
        self.logger.debug(new)
        return ET.fromstring(new)

    def main(self):
        """main"""
        self.setup_logging()
        self.load_prefs()
        self.computers = self.get_computers()
        self.logger.info("Adding computers to groups")
        for group in self.get_computer_groups():
            print(f"Processing group: {group['name']}")
            self.one_group(group)
        self.logger.info("Done the lot")


if __name__ == "__main__":
    Groups().main()
