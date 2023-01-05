from global_import import *
import base64 as b64
from near_api.providers import JsonProvider
from near_api.account import Account
import near_api

def get_validator_info(validator_id):
    """Returns validator info for the given validator_id. Expected and produced block info is for the current running epoch"""
    res_dict = {}
    payload = json.dumps({"jsonrpc": "2.0","id": "dontcare","method": "validators","params": [None]})
    curr_validators = requests.request("POST", RPC_URL_PUBLIC, headers=headers, data=payload).json()['result']['current_validators']
    val_info = next(v for v in curr_validators if v["account_id"] == validator_id)
    total_stake = sum([int(v['stake']) for v in curr_validators])
    res_dict['stake'] = val_info['stake']
    res_dict['num_expected_blocks'] = val_info['num_expected_blocks']
    res_dict['num_expected_chunks'] = val_info['num_expected_chunks']
    res_dict['num_produced_blocks'] = val_info['num_produced_blocks']
    res_dict['num_produced_chunks'] = val_info['num_produced_chunks']
    res_dict['total_stake'] = total_stake
    return res_dict

def get_transaction_by_hash(tx_hash, msg_sender):
    """Returns the transaction from NEAR RPC API. The msg.sendr is required to query the relevant shard"""
    payload = json.dumps({
        "jsonrpc": "2.0", 
        "id": "dontcare", 
        "method": "EXPERIMENTAL_tx_status",
        "params": [f"{tx_hash}", f"{msg_sender}"]
    })
    try:
        response = requests.request("POST", RPC_URL_PUBLIC, headers=headers, data=payload).json()['result']
    except:
        response = requests.request("POST", RPC_URL_PUBLIC_ARCHIVAL, headers=headers, data=payload).json()['result']
        print("Archival node was used")
    return response

# returns the epoch id for the current block if no block_height is supplied
def get_epoch_id(block_height = -1):
    payload = json.dumps({"jsonrpc": "2.0","id": "dontcare","method": "block","params": {"finality": "final"} if block_height == -1 else {"block_id": block_height}})
    response = requests.request("POST", RPC_URL_PUBLIC, headers=headers, data=payload).json()['result']['header']
    ep_id = response['epoch_id']
    return ep_id

def get_total_supply():
    payload = json.dumps({"jsonrpc": "2.0","id": "dontcare","method": "block","params": {"finality": "final"}})
    response = requests.request("POST", RPC_URL_PUBLIC, headers=headers, data=payload).json()['result']['header']
    return response['total_supply']

# If supplied with epoch start block, it will return the average block time for that epoch
def get_avg_block_time_for_epoch(start_block):
    end_block = start_block+43200
    start_time = -100 # set to 100 in order to enter the while loop and stay there for 100 tries
    end_time = -100
    blocks_to_subtract = 0

    while start_time < 0:
        # the try-except block is added for cases when the specified block was not produced
        try:
            start_time+=1
            payload = json.dumps({"jsonrpc": "2.0","id": "dontcare","method": "block","params": {"block_id": start_block}})
            print(start_block)
            start_time = requests.request("POST", RPC_URL_PUBLIC, headers=headers, data=payload).json()['result']['header']['timestamp']
        except:
            start_block+=1
            blocks_to_subtract+=1
            print("unsuccesful request. retrying...")


    while end_time < 0:
        try:
            end_time+=1            
            payload = json.dumps({"jsonrpc": "2.0","id": "dontcare","method": "block","params": {"block_id": end_block}})
            end_time = requests.request("POST", RPC_URL_PUBLIC, headers=headers, data=payload).json()['result']['header']['timestamp']
        except:
            end_block-=1
            blocks_to_subtract+=1
            print("unsuccesful request. retrying...")

    numerator = end_time - start_time
    denominator = (43200-blocks_to_subtract) * 1e9 # API returns timestamp in nanoseconds (10^-9)
    avg_bl_time = numerator/denominator 
    return avg_bl_time

def get_all_validators_ids():
    res_dict = {}
    payload = json.dumps({"jsonrpc": "2.0","id": "dontcare","method": "validators","params": [None]})
    curr_validators = requests.request("POST", RPC_URL_PUBLIC, headers=headers, data=payload).json()['result']['current_validators']
    addresses = [v['account_id'] for v in curr_validators]
    return addresses

def get_active_validator_set():
    payload = json.dumps({
    "jsonrpc": "2.0",
    "id": "dontcare",
    "method": "status",
    "params": []
    })
    response = requests.request("POST", RPC_URL_PUBLIC, headers=headers, data=payload).json()['result']['validators']
    ls = []
    for i in response:
        ls.append(i['account_id'])
    return ls

def get_block_details(block_height = -1):
    res_dict = {}
    payload = json.dumps({"jsonrpc": "2.0","id": "dontcare","method": "block","params": {"finality": "final"} if block_height == -1 else {"block_id": block_height}})
    response = requests.request("POST", RPC_URL_PUBLIC, headers=headers, data=payload).json()['result']
    
    res_dict['epoch_id'] = response['header']['epoch_id']
    res_dict['total_supply'] = response['header']['total_supply']
    res_dict['block_height'] = response['header']['height']
    res_dict['timestamp'] = response['header']['timestamp']
    res_dict['prev_epoch_last_block'] = response['header']['next_epoch_id'] # yes, weirdly enough next_epoch_id is actually the block height of the last block of the previous epoch
    return res_dict

def get_constant_vals():
    res_dict = {}
    payload = json.dumps({"jsonrpc": "2.0","id": "dontcare",
        "method": "EXPERIMENTAL_protocol_config",
        "params": {"finality": "final"}
    })
    response = requests.request("POST", RPC_URL_PUBLIC, headers=headers, data=payload).json()['result']
    res_dict['EPOCH_LENGTH'] = response['epoch_length']
    res_dict['EPOCHS_A_YEAR'] = response['num_blocks_per_year']/res_dict['EPOCH_LENGTH'] 
    res_dict['BLOCK_TIME_TARGET'] = int(365*24*60*60/int(response['num_blocks_per_year']))
    res_dict['ONLINE_THRESHOLD_MIN'] = float(response['online_min_threshold'][0]/response['online_min_threshold'][1])
    res_dict['ONLINE_THRESHOLD_MAX'] = float(response['online_max_threshold'][0]/response['online_max_threshold'][1])
    res_dict['BLOCK_PRODUCER_KICKOUT_THRESHOLD'] = int(response['block_producer_kickout_threshold'])
    res_dict['CHUNK_PRODUCER_KICKOUT_THRESHOLD'] = int(response['block_producer_kickout_threshold'])
    res_dict['GENESIS_HEIGHT'] = int(response['genesis_height'])
    return res_dict

def get_total_stake(block_num = -1):
    res_dict = {}
    if block_num == -1:
        payload = json.dumps({"jsonrpc": "2.0","id": "dontcare","method": "validators","params": [None]}) # Ideally we should be able to get this for a past block as well (according to RPC docs). But the method fails for past blocks right now
    else:
        payload = json.dumps({"jsonrpc": "2.0","id": "dontcare","method": "validators", "params": [block_num]})
    curr_validators = requests.request("POST", RPC_URL, headers=headers, data=payload).json()['result']['current_validators']
    total_stake = sum([int(v['stake']) for v in curr_validators])
    return total_stake

def get_ALL_validators_info(block_num):
    """returns produced vs expected blocks/chunks information for all the validators. The block number passed must be the last block in the epoch."""
    res_dict = {}
    payload = json.dumps({"jsonrpc": "2.0","id": "dontcare","method": "validators","params": [block_num]})
    curr_validators = requests.request("POST", RPC_URL_PUBLIC, headers=headers, data=payload).json()['result']['current_validators']
    for v in curr_validators:
        single_val = {}
        single_val['produced_blocks'] = v['num_produced_blocks']
        single_val['expected_blocks'] = v['num_expected_blocks']
        single_val['produced_chunks'] = v['num_produced_chunks']
        single_val['expected_chunks'] = v['num_expected_chunks']
        single_val['stake'] = v['stake']
        single_val['is_slashed'] = v['is_slashed']
        res_dict[v['account_id']] = single_val
    return res_dict

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
    response = requests.request("POST", RPC_URL_PUBLIC, headers=headers, data=payload).json()['result']
    return response

# param validator - account_id of the validator
# param block_id - (epoch_id OR block_height) at which we want to get the list of accounts
def get_validator_accounts(validator, block_id):
    near_provider = JsonProvider(RPC_URL_PUBLIC)    
    accounts = []
    from_index = 0
    has_more_accounts = True
    while has_more_accounts:
        TEXT = f'{{"from_index": {from_index},"limit": 500}}'
        base64 = b64.b64encode(bytes(TEXT,encoding='utf8')).decode('utf-8')
        r = near_provider.json_rpc("query", {
            "request_type": "call_function", 
            "block_id": block_id,
            "account_id": validator,
            "method_name": "get_accounts",
            "args_base64": base64
        }, timeout=60)
        lst = r.get('result')
        current_accounts = json.loads(''.join(chr(v) for v in lst))
        if len(current_accounts) == 0:
            has_more_accounts = False
        accounts += current_accounts
        from_index += 500
    return accounts

# param start_block and end_block can also be epoch IDs (I guess)
def get_rewards_for_epoch(validator, start_block, end_block):
    near_provider = JsonProvider(RPC_URL_PUBLIC_ARCHIVAL)    
    accounts_info = get_validator_accounts(validator, end_block)    
    previous_epoch_accounts_info = get_validator_accounts(validator,start_block)

    total_staked_in_beginning = 0
    total_unstaked = 0
    total_rewards = 0

    for ind, account in enumerate(accounts_info):
        current_account_id = account['account_id']
        previous_epoch_account = list(filter(lambda p_account: p_account['account_id'] == current_account_id, previous_epoch_accounts_info))

        if len(previous_epoch_account) == 0:
            rew = float(account['staked_balance'])
        else:
            total_staked_in_beginning += int(previous_epoch_account[0]["staked_balance"])
            total_unstaked += int(previous_epoch_account[0]["unstaked_balance"])
            rew = int(account["staked_balance"]) - int(previous_epoch_account[0]["staked_balance"])
            if rew < 0:
                rew = 0        
        total_rewards += rew

    # TODO: can delete the dataframe part later
    df_ls = []
    for account in accounts_info:
        current_delegator = {}
        current_account_id = account['account_id']

        previous_epoch_account = list(filter(lambda p_account: p_account['account_id'] == current_account_id, previous_epoch_accounts_info))
        if len(previous_epoch_account) == 0:
            rewards = float(account['staked_balance'])
            previous_stake_balance = 0
        else:
            rewards = int(account["staked_balance"]) - int(previous_epoch_account[0]["staked_balance"])
            previous_stake_balance = int(previous_epoch_account[0]["staked_balance"])
        
        if rewards < 0:
            rewards = 0

        current_delegator["delegator"] = current_account_id
        current_delegator["validator"] = validator
        current_delegator["balance_staked"] = int(account["staked_balance"]) / 10**24
        current_delegator["balance_unstaked"] = int(account["unstaked_balance"]) / 10**24
        current_delegator["rewards"] = rewards / 10**24   
        
        if float(current_delegator["balance_staked"]) > 0:
            current_delegator['rew/stk'] = float(current_delegator["rewards"]) / float(current_delegator["balance_staked"])
        else:
            current_delegator['rew/stk'] = 0

        df_ls.append(current_delegator)
    
    df = pd.DataFrame(df_ls)
    median_diff_in_stake = df['rew/stk'].median()
    return int(total_staked_in_beginning), int(total_rewards), median_diff_in_stake

# def v2_get_rewards_for_epoch(addr, start_block, end_block):
#     epoch_before = get_ALL_validators_info(start_block-1)  
#     epoch_curr = get_ALL_validators_info(end_block-1)

#     for i in epoch_before.keys():
#         if i == addr:
#             sum1 = int(epoch_before[i]['stake'])//1e24

#     for i in epoch_curr.keys():
#         if i == addr:
#             sum2 = int(epoch_curr[i]['stake'])//1e24

#     return int(sum1), int(sum2-sum1)

# Powered by Nearblocks.io APIs - (leave this comment in your code)
def get_recent_stake_txns_for_validator(validator_addr, start_block, end_block):
    headers = {'accept': '*/*'}
    page_no = 1

    stake_transactions = []
    fetch_more_txns = True
    added_stake_amount = 0

    while(fetch_more_txns):
        print(bcolors.OKCYAN, "Fetching deposit_and_stake Txns from Near Blocks", bcolors.ENDC)

        if page_no > 5:
            print(bcolors.FAIL, "Too many pages, something is wrong", bcolors.ENDC)
            break

        fetch_more_txns = False
        params = {'page': str(page_no), 'per_page': '25', 'order': 'desc', 'method': 'deposit_and_stake'}
        url = f'{NEAR_BLOCKS_API}/account/{validator_addr}/txns'
        response = requests.get(url, params=params, headers=headers).json()

        for txn in response['txns']:
            for action in txn['actions']:
                if action['method'] == "deposit_and_stake" and txn['block']['block_height'] > start_block and txn['block']['block_height'] < end_block:
                    stake_transactions.append(txn)
                    added_stake_amount += txn['actions_agg']['deposit']

        # fetch more transactions from API if the last transaction is more recent than the start_block
        if response['txns'][-1]['block']['block_height'] > start_block:
            fetch_more_txns = True
            page_no += 1
            time.sleep(10)

    return stake_transactions, added_stake_amount


def get_recent_STAKE_txns_for_validator(validator_addr, start_block, end_block):
    headers = {'accept': '*/*'}
    page_no = 1

    stake_transactions = []
    fetch_more_txns = True
    added_stake_amount = 0

    while(fetch_more_txns):
        print(bcolors.OKCYAN, "Fetching deposit_and_stake Txns from Near Blocks", bcolors.ENDC)

        if page_no > 15:
            print(bcolors.FAIL, "Too many pages, something is wrong", bcolors.ENDC)
            break

        fetch_more_txns = False
        params = {'page': str(page_no), 'per_page': '25', 'order': 'desc', 'method': 'deposit_and_stake'}
        url = f'{NEAR_BLOCKS_API}/account/{validator_addr}/txns'
        response = requests.get(url, params=params, headers=headers).json()

        for txn in response['txns']:
            for action in txn['actions']:
                if action['method'] == "deposit_and_stake" and txn['block']['block_height'] > start_block and txn['block']['block_height'] < end_block:
                    added_stake_amount += txn['actions_agg']['deposit']
                    stake_transactions.append({
                        "hash": txn['transaction_hash'],
                        "sender": txn['predecessor_account_id'],
                        "receipt_id" : txn['receipt_id']
                    })

        # fetch more transactions from API if the last transaction is more recent than the start_block
        if response['txns'][-1]['block']['block_height'] > start_block:
            fetch_more_txns = True
            page_no += 1
            time.sleep(10)  

    print(stake_transactions)

    total_staked_amount = 0
    
    for nearblocks_tx in stake_transactions:
        found_at_least_one_log = False
        transaction = get_transaction_by_hash(nearblocks_tx['hash'], nearblocks_tx['sender'])
        # try:
        for receipt_outcome in transaction['receipts_outcome']:
            if receipt_outcome['id'] == nearblocks_tx['receipt_id']:
                all_logs = receipt_outcome['outcome']['logs'] # Of type "someone.near deposited 120000. New"
                for unstaking_sentence_log in all_logs:
                    words = unstaking_sentence_log.split(" ")
                    if words[0] == f"@{nearblocks_tx['sender']}" and words[1] == "deposited":
                        amt = unstaking_sentence_log.split(" ")[2] # "120000."
                        amt = amt[:-1] # => removing the dot "120000"
                        total_staked_amount += int(amt)
                        found_at_least_one_log = True
                        break

        assert found_at_least_one_log == True
        # except:
        #     print(bcolors.FAIL, f"Error while fetching transaction from JSON RPC. Tx Hash : {nearblocks_tx['hash']}, sender: {nearblocks_tx['sender']}", bcolors.ENDC)


        time.sleep(2)


    return total_staked_amount


def get_recent_UNSTAKE_txns_for_validator(validator_addr, start_block, end_block):
    headers = {'accept': '*/*'}
    
    unstake_transactions = []
    total_unstaked_amount = 0
    
    fetch_more_txns = True
    page_no = 1
    while(fetch_more_txns):
        print(bcolors.OKCYAN, "Fetching unstake Txns from Near Blocks", bcolors.ENDC)
        if page_no > 5:
            print(bcolors.FAIL, "Too many pages, something is wrong", bcolors.ENDC)
            break

        fetch_more_txns = False
        params = {'page': str(page_no), 'per_page': '25', 'order': 'desc', 'method': 'unstake'}
        url = f'{NEAR_BLOCKS_API}/account/{validator_addr}/txns'
        response = requests.get(url, params=params, headers=headers).json()

        for txn in response['txns']:
            for action in txn['actions']:
                if action['method'] == "unstake" and txn['block']['block_height'] > start_block and txn['block']['block_height'] < end_block:
                    unstake_transactions.append({
                        "hash": txn['transaction_hash'],
                        "sender": txn['predecessor_account_id'],
                        "receipt_id" : txn['receipt_id']
                    })
        
        if len(response['txns']) > 0 and response['txns'][-1]['block']['block_height'] > start_block:
            fetch_more_txns = True
            page_no += 1
            time.sleep(10)


    fetch_more_txns = True
    page_no = 1
    while(fetch_more_txns):
        print(bcolors.OKCYAN, "Fetching unstake_all Txns from Near Blocks", bcolors.ENDC)
        if page_no > 5:
            print(bcolors.FAIL, "Too many pages, something is wrong", bcolors.ENDC)
            break

        fetch_more_txns = False
        params = {'page': str(page_no), 'per_page': '25', 'order': 'desc', 'method': 'unstake_all'}
        url = f'{NEAR_BLOCKS_API}/account/{validator_addr}/txns'
        response = requests.get(url, params=params, headers=headers).json()

        for txn in response['txns']:
            for action in txn['actions']:
                if action['method'] == "unstake_all" and txn['block']['block_height'] > start_block and txn['block']['block_height'] < end_block:
                    unstake_transactions.append({
                        "hash": txn['transaction_hash'],
                        "sender": txn['predecessor_account_id'],
                        "receipt_id" : txn['receipt_id']
                    })
        
        if fetch_more_txns:
            time.sleep(15)
    
    print(unstake_transactions)

    # for each of the transactions fetch from JSON RPC the information about amount unstaked
    for nearblocks_tx in unstake_transactions:
        found_at_least_one_log = False
        transaction = get_transaction_by_hash(nearblocks_tx['hash'], nearblocks_tx['sender'])
        try:
            for receipt_outcome in transaction['receipts_outcome']:
                if receipt_outcome['id'] == nearblocks_tx['receipt_id']:
                    all_logs = receipt_outcome['outcome']['logs'] # Of type "someone.near unstaking 120000. Spent XX staking shares. Total YY unstaked balance and ZZ staking shares"
                    for unstaking_sentence_log in all_logs:
                        words = unstaking_sentence_log.split(" ")
                        if words[0] == f"@{nearblocks_tx['sender']}" and words[1] == "unstaking":
                            amt = unstaking_sentence_log.split(" ")[2] # "120000."
                            amt = amt[:-1] # => removing the dot "120000"
                            total_unstaked_amount += int(amt)
                            found_at_least_one_log = True
                            break

            assert found_at_least_one_log == True
        except:
            print(bcolors.FAIL, f"Error while fetching transaction from JSON RPC. Tx Hash : {nearblocks_tx['hash']}, sender: {nearblocks_tx['sender']}", bcolors.ENDC)


        time.sleep(2)

    return total_unstaked_amount

def get_rewards_v2(addr, first_block, last_block):
    epoch_before = get_ALL_validators_info(first_block-1)  
    epoch_curr = get_ALL_validators_info(last_block-1)
    
    sum1 = 0
    sum2 = 0

    for i in epoch_before.keys():
        if i == addr:
            sum1 = int(epoch_before[i]['stake'])
    for i in epoch_curr.keys():
        if i == addr:
            sum2 = int(epoch_curr[i]['stake'])
    return int(sum2-sum1)

def get_validator_commission(validator, block_num):
    """Returns validator commisisons (in %). Block_num passed should be some recent block number"""
    near_provider = JsonProvider(RPC_URL_PUBLIC)
    TEXT = f'{{}}'
    base64 = b64.b64encode(bytes(TEXT,encoding='utf8')).decode('utf-8')
    r = near_provider.json_rpc("query", {
        "request_type": "call_function", 
        "block_id": block_num,
        "account_id": validator,
        "method_name": "get_reward_fee_fraction",
        "args_base64": base64
    }, timeout=60)
    lst = r.get('result')
    commission = json.loads(''.join(chr(v) for v in lst))
    return commission['numerator']

if __name__ == '__main__':
    print("Hello world")
    # print(int(get_rewards_v2('twinstake.poolv1.near', 82180291, 82223491)))
    
    payload = json.dumps({"jsonrpc": "2.0","id": "dontcare","method": "validators","params": [80365890]})
    curr_validators = requests.request("POST", RPC_URL_PUBLIC_ARCHIVAL, headers=headers, data=payload).json()['result']['current_validators']
    stake_ts= -1
    for v in curr_validators:
        if v['account_id'] == 'twinstake.poolv1.near':
            print(v['stake'])



    # last_block_epoch_1675 = 82223490
    # epoch_curr = 1675
    # save = []

    # for i in range(1625, 1676):
    #     payload = json.dumps({"jsonrpc": "2.0","id": "dontcare","method": "validators","params": [last_block_epoch_1675]})
    #     curr_validators = requests.request("POST", RPC_URL_PUBLIC_ARCHIVAL, headers=headers, data=payload).json()['result']['current_validators']
    #     stake_ts= -1
    #     for v in curr_validators:
    #         if v['account_id'] == 'twinstake.poolv1.near':
    #             stake_ts = v['stake']
    #             break


    #     save.append({
    #         'epoch': epoch_curr,
    #         'last_block': last_block_epoch_1675, 
    #         'stake': float(stake_ts)/1e24
    #     })
    #     print(epoch_curr)

    #     epoch_curr -= 1
    #     last_block_epoch_1675 -= 43200
    #     pd.DataFrame(save).to_csv('twinstake.csv', index=False)



# 82050691, 82093891  ==> 1672
# 82093891, 82137091  ==> 1673
# 82137091, 82180291  ==> 1674
# 82180291, 82223491  ==> 1675