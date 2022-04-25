from django.shortcuts import redirect, render
from .models import HealthRecord
from .forms import EHRForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from cryptography.fernet import Fernet
import hashlib
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

CONTRACT_ADDRESS = data['4']['EMR'][0]

f = open(f'./artifacts/deployments/4/{CONTRACT_ADDRESS}.json').read()

abi = json.loads(f)['abi']

w3 = Web3(Web3.HTTPProvider(RPC_URL))

def index(request):
    if(request.user.is_authenticated):
        record = HealthRecord.objects.filter(user=request.user)
        num = len(record)
        if(num==0):
            num+=1
            unique_id = f"HS-00{num}"
            record = HealthRecord.objects.create(user=request.user,unique_id=unique_id)
            create_ehr(unique_id)
    return render(request,'records/index.html')


def create_ehr(unique_id):
    '''
    Adds new user with unique_id and its private key
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
    -> Gets Key from Blockchain
    -> Decrypts the current data
    -> Appends EHR to current Data  
    '''
    form = EHRForm(request.POST or None)
    if(request.method == "POST"):
        if(form.is_valid()):
            name = form.cleaned_data.get('name')
            data = form.cleaned_data.get('data')

            new_record = {}
            new_record[name]=  data

            ehr_obj = request.user.record
            unique_id = ehr_obj.unique_id
            if(unique_id == None):
                messages.error(request, 'No EHR Exists!, Please Contact HealthSpace')
                return redirect("index")
            
            ehr = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)
            private_key = ehr.functions.getUserKey(unique_id).call()

            f = Fernet(private_key)

            encrypted_data = ehr_obj.ehr
            token = None
            new_entry_json = None
            if(encrypted_data):
                encrypted_data = encrypted_data.encode('utf-8')
                decrypted_data = f.decrypt(encrypted_data)

                existing_entry = json.loads(decrypted_data)
                
                existing_entry.append(new_record)

                new_entry_json = json.dumps(existing_entry).encode('utf-8')
                token = f.encrypt(new_entry_json).decode('utf-8')
            else:
                new_entry = []
                new_entry.append(new_record)
                new_entry_json = json.dumps(new_entry).encode('utf-8')

                token = f.encrypt(new_entry_json).decode('utf-8')

            ehr_obj.ehr = token
            ehr_obj.save()

            userHash = hashlib.md5(new_entry_json).hexdigest()

            nonce = w3.eth.getTransactionCount(ACCOUNT)

            # Building the transaction
            tx = ehr.functions.addUserHash(unique_id,userHash).buildTransaction(
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
            messages.success(request,"EHR Added!")    
            return redirect("index")
        messages.error(request,"Invalid Form Data!")
    return render(request,'records/create.html',{"form":form})


@login_required
def retrieve_ehr(request):
    '''
    -> Gets hashData and PrivateKey from Blockchain
    -> Verifies Authenticity
    -> Returns the decripted data
    '''
    ehr_obj = request.user.record
    unique_id = ehr_obj.unique_id
    if(unique_id == None):
        messages.error(request, 'No EHR Exists!, Please Contact HealthSpace')
        return redirect("index")
    
    ehr = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

    private_key = ehr.functions.getUserKey(unique_id).call()
    current_userHash = ehr.functions.getUserHashData(unique_id).call()
    
    f = Fernet(private_key)

    if(ehr_obj.ehr):
        encrypted_data = ehr_obj.ehr.encode('utf-8')
        decryped_data = f.decrypt(encrypted_data)
        data = json.loads(decryped_data)
    else:
        messages.error(request,"No Health Records Found!")
        return redirect('index')

    calculated_userHash = hashlib.md5(decryped_data).hexdigest()
    
    # Verifing Authenticity
    if(current_userHash == calculated_userHash):
        cal_data = []
        for s in data:
            i = list(s.keys())[0]
            j = list(s.values())[0]
            temp = {}
            temp['name'] = i
            temp['value'] = j
            cal_data.append(temp)
        return render(request,'records/ehr-list.html',{"data":cal_data})
    messages.error(request,"Authenticity Failed!, Data is Manipulated. Please Contact HealthSpace")
    return redirect('index')

