# Verimail

A Python library to check the validity of an email.

Usage:
`verimail.check(email)`

| Truth\State                    | na (0)     | regex (10) | dns (20) | helo (30) | mail (40) | rcpt (50) |
| -                              | ------     | ---------- | -------- | --------- | --------- | --------- |
| Email syntax is valid          | False      | True       | True     | True      | True      | True      |
| Email domain exists            | False      | False      | True     | True      | True      | True      |
| Email server is responsive     | False      | False      | False    | True      | True      | True      |
| SMTP "helo" command successful | False      | False      | False    | True      | True      | True      |
| SMTP "mail" command successful | False      | False      | False    | Maybe     | True      | True      |
| Email exists                   | False      | False      | False    | Maybe     | Maybe     | True      |


A frontend is provided in `frontend.py` for basic testing.
