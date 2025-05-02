import flet as ft
import re

subject_pattern = re.compile(r"Subject: (.*)\n")
from_pattern = re.compile(r"From: (.*)[\S\s]*X-From: (.*)\n")
to_pattern = re.compile(r"To: (.*)[\S\s]*X-To: (.*)\n")
date_pattern = re.compile(r"Date: (.*)\n")
body_pattren = re.compile(r"\n\n([\S\s]*)")

class Email(ft.Column):
    def __init__(self, file):
        super().__init__()
        f = open(file, errors="ignore")
        self.mail = f.read()
        f.close()
        self.mathes = {
            "date": re.match(date_pattern, self.mail),
            "subject": re.match(subject_pattern, self.mail),
            "from": re.match(from_pattern, self.mail),
            "to": re.match(to_pattern, self.mail),
            "body": re.match(body_pattren, self.mail)
        }



def main(page: ft.Page):
    t = ft.Text(value="Hello, world!", color="green")
    page.controls.append(t)
    page.update()

ft.app(main)