import smtplib
import logging
import pandas as pd
from imapclient import IMAPClient, SEEN
import email
import datetime


class SmtpClient:
    def __init__(self, credentials, host, port):
        self.cred = credentials
        self.host = host
        self.port = port

    def Connect(self):
        self.connection = smtplib.SMTP(self.host, self.port)
        self.connection.starttls()
        self.connection.login(*self.cred)
        logging.debug("SMTP connected to " + self.host + " to port " + self.port)

    def SendMail(self, mail_list, email):
        from_addr = email.get("From")
        sub = email.get("subject")
        for header in email._headers:
            email._headers.remove(header)
        email.add_header("reply-to", from_addr)
        email.add_header("From", self.cred[0])
        email.add_header("To", ", ".join(mail_list))
        email.add_header("subject", str(sub + " from: " + from_addr))
        response = self.connection.send_message(email)
        if response != {}:
            logging.warning(
                "response of the email(" + str(sub) + ") sending was " + str(response)
            )
        logging.debug(
            "Sent mail "
            + email["subject"]
            + " to addr "
            + str(mail_list)
            + " with response "
            + str(response)
        )

    def Stop(self):
        self.quit()


class GetMails:
    def __init__(self, url):
        self.url = url

    def GetMailList(self):
        data = pd.read_csv(self.url)
        datalist = data["Email"].to_list()
        logging.debug(
            "The system acquire new email list of length "
            + str(len(datalist))
            + " from url "
            + self.url
        )
        return datalist


class Imapidler:
    def __init__(
        self, IMAPHOST, USERNAME, PASSWORD, SMTPHOST, SMTPPORT, MAILURL, timeout=30
    ):
        self.HOST = IMAPHOST
        self.USERNAME = USERNAME
        self.PASSWORD = PASSWORD
        self.timeout = timeout
        self.server = IMAPClient(IMAPHOST)
        self.server.login(USERNAME, PASSWORD)
        self.smtp = SmtpClient((USERNAME, PASSWORD), SMTPHOST, SMTPPORT)
        self.maillist = GetMails(MAILURL)
        print("Logged in as " + USERNAME)

    def run(self):
        self.server.select_folder("INBOX")
        self.server.idle()
        while True:
            try:
                responses = self.server.idle_check(timeout=self.timeout)
                if responses:
                    self.server.idle_done()
                    messages = self.server.search("UNSEEN")
                    for uid, message_data in self.server.fetch(
                        messages, "RFC822"
                    ).items():
                        email_message = email.message_from_bytes(
                            message_data[b"RFC822"]
                        )
                        self.smtp.Connect()
                        self.smtp.SendMail(self.maillist.GetMailList(), email_message)
                        print(
                            "email with subject "
                            + email_message.get("subject")
                            + " sent!"
                        )
                    self.server.idle()
                print(
                    "Last idle reset at " + datetime.datetime.now().isoformat(),
                    end="\r",
                )
            except Exception as e:
                logging.error(e)
