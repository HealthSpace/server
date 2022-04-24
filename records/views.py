from django.shortcuts import render
from .models import HealthRecord
from django.contrib.auth.decorators import login_required

from cryptography.fernet import Fernet
import json
from web3 import Web3


'''
    RPC SETUP
'''
RPC_URL = "https://rinkeby.infura.io/v3/e9d544fce8bf409ca47da33037747630"

ACCOUNT =  "0x0f657448Ca3665DFD878FF0a6844cc2FeeAf927b"

PRIVATE_KEY = "0x3ed2ea0be52e9f50af157eadcb526448f14016388712d1819d41d1d9a4d4cc0b"

CHAIN_ID = 4

data = json.loads(open('./artifacts/deployments/map.json').read())

CONTRACT_ADDRESS = data['4']['EMR'][-1]

f = open(f'./artifacts/deployments/4/{CONTRACT_ADDRESS}.json').read()

abi = json.loads(f)['abi']

w3 = Web3(Web3.HTTPProvider(RPC_URL))

def index(request):
    if(request.user.is_authenticated):
        record = HealthRecord.objects.filter(user=request.user)
        num = len(record)
        if(num==0):
            unique_id = f"HS-00{num+1}" 
            record = HealthRecord.objects.create(user=request.user,unique_id=unique_id)
            create_ehr(unique_id)
    return render(request,'records/index.html')


def create_ehr(unique_id):
    '''
    add new user
    add the private key
    '''
    private_key = Fernet.generate_key()
    ehr = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

    nonce = w3.eth.getTransactionCount(ACCOUNT)

    # Building the transaction
    tx = ehr.functions.addUserKey(unique_id,private_key).buildTransaction(
        {
        "chainId": CHAIN_ID,
        "from": ACCOUNT,
        "nonce": nonce,
        "gasPrice": w3.eth.gas_price,
        }
    )

    # Signing the transaction
    signed_tx = w3.eth.account.sign_transaction(tx,private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    # executing the transaction
    tx_receipt =  w3.eth.waitForTransactionReceipt(tx_hash)
    

@login_required
def add_ehr(request):
    '''
    -> with the key, get the data from blockchain
    -> decript the current data
    -> modifiy the dict and store it again
    -> update hashData to blockchain
    '''
    pass


@login_required
def retrieve_ehr(request):
    '''
    -> get hashData blockchain
    -> get key blockhain
    -> decript it and hash it
    -> compare the two hashes (verify authticity)
    -> return the decripted data
    '''
    ehr_obj = HealthRecord.objects.filter()
    pass


def verify_authenticity():
    pass


