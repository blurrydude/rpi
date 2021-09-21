import json
from datetime import datetime
import os
import smtplib

class SmarterLog:
    @staticmethod
    def log(origin, message):
        source_dir = os.path.dirname(os.path.realpath(__file__))+"/"
        if type(message) is not type(""):
            message = json.dumps(message)
        timestamp = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        logfiledate = datetime.now().strftime("%Y%m%d%H")
        logfile = source_dir + "logs/SmarterCircuits_"+logfiledate+".log"
        entry = timestamp + " [" + origin + "]: " + message + "\n"
        print(entry)
        try:
            if os.path.exists(logfile):
                append_write = 'a' # append if already exists
            else:
                append_write = 'w' # make a new file if not

            with open(logfile, append_write) as write_file:
                write_file.write(entry)
        except:
            print("shit")

    @staticmethod
    def send_email(to, subject, body):
        email_text = """\
        From: %s
        To: %s
        Subject: %s

        %s
        """ % ('house@smartercirctuis.com', ", ".join(to), subject, body)

        try:
            smtp_server = smtplib.SMTP('smtp.mailgun.com', 587)
            smtp_server.starttls()
            smtp_server.login("postmaster@sandboxab162af263364a6a843fe4c0fc03483f.mailgun.org", "0a569105db8ddbdfb17ee4b9e4f150f2-45f7aa85-029a5394")
            smtp_server.sendmail('house@smartercirctuis.com', to, email_text)
            smtp_server.quit()
            SmarterLog.log("SmarterLogging", "Email sent successfully!")
        except Exception as ex:
            SmarterLog.log("SmarterLogging", "Failed to send email notification: "+str(ex))