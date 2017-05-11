#!/usr/bin/python3

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

import login

def format_mail(fromaddr, toaddr, text, attach):

    msg = MIMEMultipart()

    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Wheather Forecast"

    #body = "Python test mail"
    msg.attach(MIMEText(text, 'html'))

    fp = open(attach, 'rb')
    img_file = MIMEImage(fp.read())
    fp.close()

    img_file.add_header('Content-ID', '<image1>')
    msg.attach(img_file)

    return msg.as_string()

def send(fromaddr, toaddr, msg, attach):

    server = smtplib.SMTP('smtp.gmail.com', 587)

    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login(login.mail, login.pw)

    text = format_mail(fromaddr, toaddr, msg, attach)

    server.sendmail(fromaddr, toaddr, text)

    return 0
