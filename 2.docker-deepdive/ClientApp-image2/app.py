import requests
import time

def main():
    print("Client App Started")
    for i in range(5): # 5 tries
        try:
            response=requests.get("http://server_app:5000/data")

            if response.status_code==200:
                print(f"Response from Server App : {response.text}")
                break
            
        except requests.exceptions.RequestException:
            print(f"Attempt {i+1}, Server is not ready..yet trying!")
            time.sleep(2)
    

if __name__=="__main__":
    main()
    