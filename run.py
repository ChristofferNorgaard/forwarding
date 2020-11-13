from forward import *
import logging
import json
import datetime
import sys

file_loc = "config.json"
if len(sys.argv) > 1:
    file_loc = sys.argv[1]
logging.basicConfig(
    level=logging.WARNING,
    filename="system" + str(datetime.date.today()) + ".log",
    filemode="a",
)
logging.getLogger().addHandler(logging.StreamHandler())
with open(file_loc) as json_data_file:
    config = json.load(json_data_file)
creds = (config["credentials"]["user"], config["credentials"]["pass"])
m = Imapidler(
    config["imap"]["host"],
    config["credentials"]["user"],
    config["credentials"]["pass"],
    config["smtp"]["host"],
    config["smtp"]["port"],
    config["mail_list"]["url"],
    config["admin-mail"],
)
try:
    print("You are going to be sendig every mail to:")
    for i in m.maillist.GetMailList():
        print("     " + i)
    m.run()
except KeyboardInterrupt:
    pass
