import requests
import time

URL = "http://localhost:8080/api/info"
REQUESTS_TO_SEND = 6

# ANSI escape codes for colors
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

print(f"{Colors.HEADER}{Colors.BOLD}===================================================={Colors.ENDC}")
print(f"{Colors.HEADER}{Colors.BOLD}      ⚖️  RateGuard Load Balancing Test ⚖️      {Colors.ENDC}")
print(f"{Colors.HEADER}{Colors.BOLD}===================================================={Colors.ENDC}\n")

print(f"{Colors.OKCYAN}[INFO]{Colors.ENDC} Gateway URL: {URL}")
print(f"{Colors.OKCYAN}[INFO]{Colors.ENDC} Sending {REQUESTS_TO_SEND} sequential requests with a 1.5s delay to avoid rate limits.")
print(f"{Colors.OKCYAN}[INFO]{Colors.ENDC} Watch the 'Backend Host' value change as NGINX round-robins across Docker replicas.\n")

for i in range(REQUESTS_TO_SEND):
    try:
        response = requests.get(URL)
        if response.status_code == 200:
            data = response.json()
            hostname = data.get('hostname', 'Unknown')
            msg = data.get('message', '')
            print(f"[{Colors.OKBLUE}Req #{i+1:02d}{Colors.ENDC}] {Colors.OKGREEN}✔ 200 OK{Colors.ENDC} | Backend Host: {Colors.WARNING}{hostname}{Colors.ENDC}")
            # Only print the explanation once
            if i == 0:
                print(f"          ↳ {Colors.OKCYAN}Note: '{hostname}' is the internal Docker replica ID responding to this request.{Colors.ENDC}")
        elif response.status_code == 429:
            print(f"[{Colors.OKBLUE}Req #{i+1:02d}{Colors.ENDC}] {Colors.FAIL}✖ 429 Too Many Requests{Colors.ENDC} (Rate Limit Hit)")
        else:
            print(f"[{Colors.OKBLUE}Req #{i+1:02d}{Colors.ENDC}] {Colors.FAIL}! Failed with {response.status_code}{Colors.ENDC}")
    except requests.exceptions.ConnectionError:
        print(f"[{Colors.OKBLUE}Req #{i+1:02d}{Colors.ENDC}] {Colors.FAIL}✖ Error: Unable to connect to gateway{Colors.ENDC}")
    except Exception as e:
        print(f"[{Colors.OKBLUE}Req #{i+1:02d}{Colors.ENDC}] {Colors.FAIL}✖ Error: {e}{Colors.ENDC}")
    
    # Wait to allow token refill and avoid rate limits
    if i < REQUESTS_TO_SEND - 1:
        time.sleep(1.5)

print(f"\n{Colors.OKGREEN}{Colors.BOLD}✅ Load Balancing Test Completed!{Colors.ENDC}")
