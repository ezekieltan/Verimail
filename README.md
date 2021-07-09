# Verimail

A Python library to check the validity of an email.

Usage:
`verimail.check(email)`

Returns a state which certain truths can be determined about the email address. 

| Truth\State                    | na (0)     | regex (10) | dns (20) | helo (30) | mail (40) | rcpt (50) |
| -                              | ------     | ---------- | -------- | --------- | --------- | --------- |
| Email syntax is valid          | False      | True       | True     | True      | True      | True      |
| Email domain exists            | False      | False      | True     | True      | True      | True      |
| Email server is responsive     | False      | False      | False    | True      | True      | True      |
| SMTP "helo" command successful | False      | False      | False    | True      | True      | True      |
| SMTP "mail" command successful | False      | False      | False    | Maybe     | True      | True      |
| Email exists                   | False      | False      | False    | Maybe     | Maybe     | True      |

A basic frontend is provided in `frontend.py` for testing.

Output will be unreliable when running code from a residential IP address as such IPs are likely to be on blacklists, resulting in denied commands.
