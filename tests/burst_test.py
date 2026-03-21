import threading
import requests
import time
import sys

URL = "http://localhost:8080/api/test"
CONCURRENT_REQUESTS = 10

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
print(f"{Colors.HEADER}{Colors.BOLD}        🚀 RateGuard Burst Capacity Test 🚀       {Colors.ENDC}")
print(f"{Colors.HEADER}{Colors.BOLD}===================================================={Colors.ENDC}\n")

print(f"{Colors.OKCYAN}[INFO]{Colors.ENDC} Gateway URL: {URL}")
print(f"{Colors.OKCYAN}[INFO]{Colors.ENDC} Sending {CONCURRENT_REQUESTS} concurrent requests...\n")

def make_request(request_id):
    try:
        response = requests.get(URL)
        if response.status_code == 200:
            print(f"[{Colors.OKBLUE}Req #{request_id:02d}{Colors.ENDC}] {Colors.OKGREEN}✔ Status 200{Colors.ENDC} - Request Allowed (Token consumed)")
        elif response.status_code == 429:
            print(f"[{Colors.OKBLUE}Req #{request_id:02d}{Colors.ENDC}] {Colors.FAIL}✖ Status 429{Colors.ENDC} - Rate Limited (Bucket empty)")
        else:
            print(f"[{Colors.OKBLUE}Req #{request_id:02d}{Colors.ENDC}] {Colors.WARNING}! Status {response.status_code}{Colors.ENDC}")
    except requests.exceptions.ConnectionError:
        print(f"[{Colors.OKBLUE}Req #{request_id:02d}{Colors.ENDC}] {Colors.FAIL}✖ Error: Unable to connect to gateway{Colors.ENDC}")
    except Exception as e:
        print(f"[{Colors.OKBLUE}Req #{request_id:02d}{Colors.ENDC}] {Colors.FAIL}✖ Error: {e}{Colors.ENDC}")

threads = []
for i in range(CONCURRENT_REQUESTS):
    t = threading.Thread(target=make_request, args=(i+1,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print(f"\n{Colors.WARNING}[WAIT]{Colors.ENDC} Sleeping for 6 seconds to allow token bucket refill...\n")
for i in range(6, 0, -1):
    sys.stdout.write(f"\rTime remaining: {i}s ")
    sys.stdout.flush()
    time.sleep(1)
sys.stdout.write("\rTime remaining: 0s \n\n")

print(f"{Colors.OKCYAN}[INFO]{Colors.ENDC} Sending another request after bucket refill...")
make_request(CONCURRENT_REQUESTS + 1)

print(f"\n{Colors.OKGREEN}{Colors.BOLD}✅ Burst Test Completed!{Colors.ENDC}")
