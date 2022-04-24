from django.shortcuts import render
from .models import HealthRecord

from cryptography.fernet import Fernet
import json
from web3 import Web3

RPC_URL = "https://mainnet.infura.io/v3/e9d544fce8bf409ca47da33037747630"

ACCOUNT =  "0x0f657448Ca3665DFD878FF0a6844cc2FeeAf927b"

PRIVATE_KEY = "0x3ed2ea0be52e9f50af157eadcb526448f14016388712d1819d41d1d9a4d4cc0b"

data = json.loads(open('./artifacts/deployments/map.json').read())

CONTRACT_ADDRESS = data['4']['EMR'][-1]
# print(CONTRACT_ADDRESS)

f = open(f'./artifacts/deployments/4/{CONTRACT_ADDRESS}.json').read()

abi = json.loads(f)

w3 = Web3(Web3.HTTPProvider(RPC_URL))

def index(request):
    if(request.user.is_authenticated):
        record = HealthRecord.objects.filter(user=request.user)
        print(record)
        if(len(record)==0):
            print(1)
    return render(request,'records/index.html')

def create_ehr(request):
    '''
    add new user
    add the private key
    '''
    private_key = Fernet.generate_key()
    print((private_key).decode("utf-8"))
    f = Fernet(private_key)
    data = {
        "blood_grp":'A',
        'sugar':"12"
    }
    encripted_data = json.dumps(data)
    encripted_data_encoded = encripted_data.encode('utf-8')
    token = f.encrypt(encripted_data_encoded)
    print(token)


def add_ehr(request):
    '''
    -> with the key, get the data from blockchain
    -> decript the current data
    -> modifiy the dict and store it again
    -> update hashData to blockchain
    '''
    pass


def retrieve_ehr(request):
    '''
    -> get hashData blockchain
    -> get key blockhain
    -> decript it and hash it
    -> compare the two hashes (verify authticity)
    -> return the decripted data
    '''
    pass


def verify_authenticity():
    pass


