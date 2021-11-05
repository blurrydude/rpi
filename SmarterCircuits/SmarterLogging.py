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
    def send_email(smtp_user, smtp_pass, to, subject, body):
        # email_text = """\
        # From: %s
        # To: %s
        # Subject: %s

        # %s
        # """ % ('house@smartercircuits.com', to, subject, body)

        # try:
        #     smtp_server = smtplib.SMTP('smtp.mailgun.com', 587)
        #     smtp_server.starttls()
        #     smtp_server.login(smtp_user, smtp_pass)
        #     smtp_server.sendmail('house@smartercirctuis.com', [to], email_text)
        #     smtp_server.quit()
        #     SmarterLog.log("SmarterLogging", "Email sent successfully!")
        # except Exception as ex:
        #     SmarterLog.log("SmarterLogging", "Failed to send email notification: "+str(ex))
        doNothing = True