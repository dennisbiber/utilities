import smtplib
from email.message import EmailMessage
import os

def sendEmail():
    email = EmailMessage()
    email['from'] = input("Enter your name: ")
    email['to'] = input("Email address of recipient: ")
    email['subject'] = input("Subject: ")

    email.set_content(input("Msg Content: "))

    with smtplib.SMTP(host='smtp.gmail.com', port=587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(input("Enter your email: "),input("Enter your password: "))
        smtp.send_message(email)
        print("Email send")

def main():
    email = sendEmail()

if __name__ == "__main__":
    main()