from global_import import *

def get_validator_info(validator_id):
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

# return the average block time for the past 43200 block (not necessarily in the same epoch)
def get_avg_block_time_recent():
    payload = json.dumps({"jsonrpc": "2.0","id": "dontcare","method": "block","params": {"finality": "final"}})
    response = requests.request("POST", RPC_URL_PUBLIC, headers=headers, data=payload).json()['result']['header']
    curr_height = response['height']
    end_time = response['timestamp']

    start_block = curr_height - 43200
    start_time = -1
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

    numerator = end_time - start_time
    denominator = (43200-blocks_to_subtract) * 1e9 # API returns timestamp in nanoseconds (10^-9)
    avg_bl_time = numerator/denominator 
    return avg_bl_time


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

# returns 1 if all the values are as expected. 0 otherwise.
def confirm_constant_vals():
    # Expected values
    EPOCHS_A_YEAR = 730
    EPOCH_LENGTH = 43200
    ONLINE_THRESHOLD_MIN = 0.90
    ONLINE_THRESHOLD_MAX = 0.99
    BLOCK_PRODUCER_KICKOUT_THRESHOLD = 90
    BLOCK_TIME_TARGET = 1
    # Verification of values 
    all_ok = True

    payload = json.dumps({"jsonrpc": "2.0","id": "dontcare",
        "method": "EXPERIMENTAL_protocol_config",
        "params": {"finality": "final"}
    })
    response = requests.request("POST", RPC_URL_PUBLIC, headers=headers, data=payload).json()['result']

    epoch_length = response['epoch_length']
    if epoch_length != EPOCH_LENGTH:
        print(bcolors.FAIL, "ERR: Blocks per epoch. Expected: ", EPOCH_LENGTH, ". Actual: ", epoch_length, bcolors.ENDC)
        all_ok = False

    epochs_per_year = response['num_blocks_per_year']/EPOCH_LENGTH
    if epochs_per_year != EPOCHS_A_YEAR:
        print(bcolors.FAIL, "ERR: Epochs per year. Expected: ", EPOCHS_A_YEAR, ". Actual: ", epochs_per_year, bcolors.ENDC)
        all_ok = False

    target_block_time = int(365*24*60*60/int(response['num_blocks_per_year']))
    if target_block_time != BLOCK_TIME_TARGET:
        print(bcolors.FAIL, "ERR: Target block time. Expected: ", BLOCK_TIME_TARGET, ". Actual: ", target_block_time, bcolors.ENDC)
        all_ok = False

    min_online_threshold = float(response['online_min_threshold'][0]/response['online_min_threshold'][1])
    if min_online_threshold != ONLINE_THRESHOLD_MIN:
        print(bcolors.FAIL, "ERR: Online minimum threshold. Expected: ", ONLINE_THRESHOLD_MIN, ". Actual: ", min_online_threshold, bcolors.ENDC)
        all_ok = False

    max_online_threshold = float(response['online_max_threshold'][0]/response['online_max_threshold'][1])
    if max_online_threshold != ONLINE_THRESHOLD_MAX:
        print(bcolors.FAIL, "ERR: Online minimum threshold. Expected: ", ONLINE_THRESHOLD_MAX, ". Actual: ", max_online_threshold, bcolors.ENDC)
        all_ok = False

    max_online_threshold = int(response['block_producer_kickout_threshold'])
    if max_online_threshold != BLOCK_PRODUCER_KICKOUT_THRESHOLD:
        print(bcolors.FAIL, "ERR: Block producer kickout threshold. Expected: ", BLOCK_PRODUCER_KICKOUT_THRESHOLD, ". Actual: ", max_online_threshold, bcolors.ENDC)
        all_ok = False

    return int(all_ok)

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