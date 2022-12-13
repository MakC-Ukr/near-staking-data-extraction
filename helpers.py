from global_import import *

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
    start_time = -1
    end_time = -1
    blocks_to_subtract = 0

    while start_time < 0:
        # the try-except block is added for cases when the specified block was not produced
        try:
            payload = json.dumps({"jsonrpc": "2.0","id": "dontcare","method": "block","params": {"block_id": start_block}})
            start_time = requests.request("POST", RPC_URL_PUBLIC, headers=headers, data=payload).json()['result']['header']['timestamp']
        except:
            start_block+=1
            blocks_to_subtract+=1
            print("unsuccesful request. retrying...")


    while end_time < 0:
        try:
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
    response = requests.request("POST", RPC_URL, headers=headers, data=payload).json()['result']
    return response

if __name__ == '__main__':
    print("Hello world")