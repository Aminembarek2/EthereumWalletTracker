from requests import get, exceptions
from matplotlib import pyplot as plt
from  datetime import datetime

API_KEY = "UCAZF4WU4J9VVMBUJ4MP5CEDCAYQB2RJZ7" # put your API_KEY
B_URL = "https://api.etherscan.io/api"
address = "0x71C7656EC7ab88b098defB751B7401B5f6d8976F" 
ETH = 10**18

def make_url(module,action,adress,**kwargs):
    url = B_URL + f"?module={module}&action={action}&address={adress}&apikey={API_KEY}"

    for key , value in kwargs.items():
        url += f"&{key}={value}"
    return url

def get_data(url):
    try:
        response = get(url)
        data = response.json()
        return data
    except exceptions.RequestException as e:  
        raise SystemExit(e)

#get the current balance
def get_current_balance(address):
    get_url = make_url("account", "balance" ,address, tag= "latest")
    data = get_data(get_url)

    if data['status'] == '1':
        value = int(data['result']) / ETH
    else:
        value = data['result']
    return value

# get all the data (internal and normal transactions)
def get_transactions(address):
    tr_url = make_url("account", "txlist", address, startblock = "0", endblock = "99999999", page="1", offset="10000", sort="asc") #tr : transactions
    normal_tr_data = get_data(tr_url)

    if normal_tr_data['status'] == '0':
        normal_tr_data = normal_tr_data['message']
        print(normal_tr_data)
        exit()
    else:
        normal_tr_data = normal_tr_data['result']
    
    #internal tr 
    internal_tr_url = make_url("account", "txlistinternal", address, startblock = "0", endblock = "99999999", page="1", offset="10000", sort="asc")
    internal_tr_data = get_data(internal_tr_url)

    if internal_tr_data['status'] == '0':
        internal_tr_data = internal_tr_data['message']
        print(internal_tr_data)
        exit()
    else:
        internal_tr_data = internal_tr_data['result']

    normal_tr_data.extend(internal_tr_data)
    normal_tr_data.sort(key=lambda x: int(x['timeStamp']))

    return normal_tr_data
    
def wallet_transactions(address):
    data = get_transactions(address)
    balance = get_current_balance(address)

    current_balance = 0
    balances = []
    times = []

    for tr in data :
        to_addr = tr["to"]
        value = int(tr["value"])/ ETH

        if "gasPrice" in tr:
            gas = int(tr["gasUsed"]) * int(tr["gasPrice"]) / ETH
        else:
            gas = int(tr["gasUsed"]) / ETH

        time = datetime.fromtimestamp(int(tr["timeStamp"]))

        if to_addr.lower() == address.lower():
            current_balance += value
        else:
            current_balance -= value + gas

        times.append(time)
        balances.append(current_balance)

    plt.plot(times,balances)
    plt.show()
    
    print("Current Balance:",balance)

    return 

wallet_transactions(address)