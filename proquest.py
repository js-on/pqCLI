from bs4 import BeautifulSoup as bs4
from tabulate import tabulate
from typing import Tuple, Any
from colorama import Fore
import requests
import getpass
import keyring
import config
import re

RED = Fore.RED
RESET = Fore.RESET
GREEN = Fore.GREEN
YELLOW = Fore.YELLOW

BASE_URL = config.base_url
CONVERT = {
    "Autoren": "Autor"
}


def check_condition(l: Any, r: Any, msg: str, ex: bool):
    """Check whether left side equals right side, 
    print error if not and exit if necessary

    Args:
        l (Any): left side of expression
        r (Any): right side of expression
        msg (str): error message
        ex (bool): exit with err code 1
    """
    if l == r:
        print(RED + msg + RESET)
        if ex:
            exit(1)


def print_success(msg: str, end='\n'):
    """print success messages

    Args:
        msg (str): success message to print
    """
    print(GREEN + msg + RESET)


def print_error(msg: str, end='\n'):
    """print errors in red color

    Args:
        msg (str): error message to print
    """
    print(RED + msg + RESET)


def print_warning(msg: str, end='\n'):
    """print warnings in yellow color

    Args:
        msg (str): error message to print
    """
    print(YELLOW + msg + RESET)


def store_creds_in_keyring(service: str, username: str):
    """Store credentials in keyring

    Args:
        service (str): service name to store creds in
        username (str): username for which the password is for
    """
    print_warning("No credentials found in keyring.\nStarted account setup!")
    password = getpass.getpass(f"Password for account {username}: ")
    keyring.set_password(service, username, password)
    print_success(
        f"Password for {username} was successfully stored in key {service}.")


def get_creds_from_keyring() -> Tuple[str, str]:
    """automatically fetch creds from keyring

    Returns:
        Tuple[str, str]: username and password
    """
    username = config.username
    check_condition(username, "", "Username can't be empty.", True)
    service = "proquest"
    check_condition(service, "", "service can't be empty.", True)
    password = keyring.get_password(service, username)
    if not password:
        store_creds_in_keyring(service, username)
        return get_creds_from_keyring()
    return (username, password)


def ask_creds() -> Tuple[str, str]:
    """manually ask for credentials

    Returns:
        Tuple[str, str]: username and password
    """
    username = input("Enter your ProQuest username: ")
    password = getpass.getpass("Enter your ProQuest password: ")
    return (username, password)


def init_proquest_session() -> Tuple[requests.Session, dict]:
    """return authenticated ProQuest session

    Returns:
        Tuple[requests.Session, dict]: authenticated session, user object
    """
    check_condition(config.institution, "", "Value for institution can't be empty.", True)
    s = requests.Session()
    s.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"
    url = BASE_URL + f"/auth/lib/{config.institution}/login.action"
    s.get(url)
    if config.use_keyring:
        username, password = get_creds_from_keyring()
    else:
        username, password = ask_creds()
    payload = {
        "username": username,
        "password": password,
        "siginButton": "Anmelden",
        "mode": "regular"
    }
    s.post(url, data=payload)
    data = s.get(BASE_URL + "/favicon.ico")
    soup = bs4(data.text, "lxml")
    userId, _, userTypeID = re.findall(
        r'(\d{4,})', str(soup.findAll(id="searchUserData")[0]))
    username = username.split("@")[0]
    user = {
        "username": username[0].upper() + username.split(".")[1].capitalize(),
        "userId": userId,
        "userTypeID": userTypeID,
        "userState": "INDIVIDUAL"
    }
    return (s, user)


def query_by_docID(s: requests.Session, inp: int, user: dict):
    """return content of book detail page

    Args:
        s (requests.Session): authenticated ProQuest session
        inp (int): docID of the book
        user (dict): user obj
    """
    query = BASE_URL + f"/lib/{config.institution}/detail.action?docID={inp}"
    res = s.get(query)
    extract_details(res.text)


def extract_details(content: str):
    """extract details from page details (HTML)

    Args:
        content (str): html content
    """
    soup = bs4(content, "lxml")
    bib_container = soup.findAll(id="bib-container")
    bib_labels = bib_container[0].findAll(class_="bib-label")
    bib_fields = bib_container[0].findAll(class_="bib-field")
    details = {}
    for label, field in zip(bib_labels, bib_fields):
        if label.text.strip() in CONVERT:
            label = CONVERT[label.text.strip()]
        else:
            label = label.text.strip()
        details[label] = field.text.strip()
    format_details(details)


def format_details(details: dict):
    """print details as table

    Args:
        details (dict): [description]
    """
    data = [[i, details[i]] for i in details.keys()]
    print(tabulate(data))
    print(f"Cite in {config.default_style} style: ", end='')
    print_success(get_cite(details))
    print()


def get_cite(details: dict):
    """create cite from cite template

    Args:
        details (dict): dict with doc details

    Returns:
        [type]: formatted cite
    """
    template = config.styles.get(config.default_style, None)
    check_condition(
        template, None, f"Default style \"{config.default_style}\" not found in styles.", True)
    text = template
    for val in details.keys():
        placeholder = f"${val}$"
        if placeholder in text:
            text = text.replace(placeholder, details[val])
    return text


def logout(s: requests.Session, user: dict, inp: Any):
    """Logout from current session and exit

    Args:
        s (requests.Session): authenticated session
        user (dict): user object
        inp (Any): user input
    """
    url = BASE_URL + \
        f"/auth/lib/{config.institution}/logout.action?userName={user['username']}&userId={user['userId']}&userTypeID={user['userTypeID']}&UserState={user['userState']}"
    s.get(url)
    print_success("Thanks for using pqCLI, c u soon...")
    exit(0)


def help(s: requests.Session, user: dict, inp: Any):
    """Print help based on command dict and referenced function docstrings

    Args:
        s (requests.Session): authenticated session
        user (dict): user object
        inp (Any): user input
    """
    # TODO: Prettier formatting (e.g. h|help module.__doc__)
    table_headers = ["command", "description"]
    table_data = []
    for cmd in COMMANDS:
        table_data.append([cmd, COMMANDS[cmd].__doc__.split("\n")[0]])
    print(tabulate(tabular_data=table_data, headers=table_headers))

def delete_creds_from_keyring(s: requests.Session, user: dict, inp: Any):
    """Remove credentials from keyring

    Args:
        s (requests.Session): authenticated session
        user (dict): user object
        inp (Any): user input
    """
    print_warning("You are going to delete your credentials from the keyring.")
    print_warning("You need to set them up again on the next run.")
    print_error("Are you sure? (yY|nN): ", end='')
    answer = input()
    if answer.lower() == "y":
        keyring.delete_password("proquest", config.username)
        print_success(f"Successfully deleted credentials for user {user['username']}.")
    else:
        print_warning("Operation canceled.")

def exec(inp: str, s: requests.Session, user: dict):
    """Check CLI input and trigger corresponding actions

    Args:
        inp (str): user input
        s (requests.Session): authenticated session
        user (dict): user obj
    """
    if inp in COMMANDS.keys():
        COMMANDS[inp](inp=inp, s=s, user=user)
    else:
        for regex, action in ACTIONS.items():
            if regex.match(inp):
                action(inp=inp, s=s, user=user)


def main():
    s, user = init_proquest_session()
    while True:
        inp = input(f"{user['username']}@ProQuest:~$ ")
        exec(inp, s, user)


COMMANDS = {
    "q": logout,
    "quit": logout,
    "h": help,
    "help": help,
    "d": delete_creds_from_keyring,
    "unregister": delete_creds_from_keyring,
}
ACTIONS = {
    re.compile(r'^\d{4,10}$'): query_by_docID,
}

if __name__ == '__main__':
    main()
