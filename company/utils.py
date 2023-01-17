import random
import string


def get_template(file: str):
    return 'company/{}.html'.format(file)


def get_tech_template(file: str):
    return f"tech/{file}.html"


def get_ticket_code():
    num = '0123456789'
    letters = string.ascii_letters
    raw = num + letters
    return ''.join(random.sample(raw, 20))
