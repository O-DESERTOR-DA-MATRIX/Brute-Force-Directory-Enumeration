import requests


def checkurl(ip, wordlist): 
    try:
        # Open the wordlist file
        with open(wordlist, 'r') as file:
            reading = file.read()
            spliting = reading.split()  # Split the content of the wordlist by spaces
            
            # Iterate through each directory/file from the wordlist
            for objectss in spliting:
                
               
                
                try:
                    url = f"https://{ip}/{objectss}"  # Construct the URL
                    r = requests.get(url, timeout=2)  # Timeout added to avoid hanging
                    
                    if r.status_code == 200:
                        print(f"URL found: {url}")
                    elif r.status_code == 403:
                        print(f"URL forbidden: {url}")
                    
                except:
                    pass
            
    except FileNotFoundError:
        print("Ip Address or Wordlist path not found, verify your Ip Address or your wordlist path and try again.")
        
if __name__ == "__main__":
    # Ask for IP and wordlist path
    ip = input("Type your IP or domain: ")
    wordlist = input("Type your wordlist path: ")
    
    # Call the URL checking function
    checkurl(ip, wordlist)

