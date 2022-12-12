from global_import import *
from datetime import datetime
currentDateAndTime = datetime.now()
currentTime = currentDateAndTime.strftime("%H:%M")
def get_all_validators_ids():
    res_dict = {}
    payload = json.dumps({"jsonrpc": "2.0","id": "dontcare","method": "validators","params": [None]})
    curr_validators = requests.request("POST", RPC_URL_PUBLIC, headers=headers, data=payload).json()['result']['current_validators']
    addresses = [v['account_id'] for v in curr_validators]
    return addresses

def get_acc_info(account_id):
    payload = json.dumps({
    "jsonrpc": "2.0",
    "id": "dontcare",
    "method": "query",
    "params": {
        "request_type": "view_account",
        "finality": "final",
        "account_id": str(account_id)
    }})
    response = requests.request("POST", RPC_URL, headers=headers, data=payload).json()['result']
    return response


def get_acc_info_for_block(account_id, block_height):
    payload = json.dumps({
    "jsonrpc": "2.0",
    "id": "dontcare",
    "method": "query",
    "params": {
        "request_type": "view_account",
        "block_id": block_height,
        "account_id": str(account_id)
    }})
    response = requests.request("POST", RPC_URL, headers=headers, data=payload).json()['result']
    return response

addresses = get_all_validators_ids()
df_ls = []

#
# Part 1  - get current validators' account info
#

# for addr in tqdm(addresses):
#     acc_info = get_acc_info(addr)
#     df_ls.append({
#         "account_id": addr,
#         "amount": acc_info['amount'],
#         "locked": acc_info['locked']
#     })

# pd.DataFrame(df_ls).to_csv(f"data_cache/all_validators-{currentTime}.csv", index=False)


#
# Part 2  - get all validators' info before and after 77082691
#
for addr in tqdm(addresses[:10]):
    try:
        before_info = get_acc_info_for_block(addr, 80020291) # Assuming these block exist
        after_info = get_acc_info_for_block(addr, 80023891)
        df_ls.append({
            "account_id": addr,
            "before_amount": float(before_info['amount']),
            "before_locked": float(before_info['locked']),
            "after_amount": float(after_info['amount']),
            "after_locked": float(after_info['locked']),
        })
    except:
        print(bcolors.FAIL, " Error for ", addr, bcolors.ENDC)

pd.DataFrame(df_ls).to_csv(f"data_cache/all_validators-before_and_after_edge_block.csv", index=False)