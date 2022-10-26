# doesn't work with block-height. Though ideally it should (accoridng to RPC)
def TEST_get_validator_info(validator_id, block_height = -1):
    res_dict = {}
    payload = json.dumps({"jsonrpc": "2.0","id": "dontcare","method": "validators","params": [None] if block_height == -1 else [block_height]})
    curr_validators = requests.request("POST", RPC_URL, headers=headers, data=payload).json()['result']['current_validators']
    val_info = next(v for v in curr_validators if v["account_id"] == validator_id)
    res_dict['stake'] = val_info['stake']
    res_dict['num_expected_blocks'] = val_info['num_expected_blocks']
    res_dict['num_expected_chunks'] = val_info['num_expected_chunks']
    res_dict['num_produced_blocks'] = val_info['num_produced_blocks']
    res_dict['num_produced_chunks'] = val_info['num_produced_chunks']
    return res_dict


# If supplied with epoch start block, it will return the average block time for that epoch
def TEST_get_avg_block_time_for_epoch(start_block):
    end_block = start_block+43200
    start_time = -1
    end_time = -1
    blocks_to_subtract = 0

    while start_time < 0:
        # the try-except block is added for cases when the specified block was not produced
        try:
            payload = json.dumps({"jsonrpc": "2.0","id": "dontcare","method": "block","params": {"block_id": start_block}})
            start_time = requests.request("POST", RPC_URL, headers=headers, data=payload).json()['result']['header']['timestamp']
        except:
            start_block+=1
            blocks_to_subtract+=1
            print("unsuccesful request. retrying...")


    while end_time < 0:
        try:
            payload = json.dumps({"jsonrpc": "2.0","id": "dontcare","method": "block","params": {"block_id": end_block}})
            end_time = requests.request("POST", RPC_URL, headers=headers, data=payload).json()['result']['header']['timestamp']
        except:
            end_block-=1
            blocks_to_subtract+=1
            print("unsuccesful request. retrying...")

    numerator = end_time - start_time
    denominator = (43200-blocks_to_subtract) * 1e9 # API returns timestamp in nanoseconds (10^-9)
    avg_bl_time = numerator/denominator 
    return avg_bl_time

# Only retrieves total stake amount
def get_total_stake():
    res_dict = {}
    payload = json.dumps({"jsonrpc": "2.0","id": "dontcare","method": "validators","params": [None]}) # Ideally we should be able to get this for a past block as well (according to RPC docs). But the method fails for past blocks right now
    curr_validators = requests.request("POST", RPC_URL, headers=headers, data=payload).json()['result']['current_validators']
    total_stake = sum([int(v['stake']) for v in curr_validators])
    return total_stake

def get_validator_info(validator_id):
    res_dict = {}
    payload = json.dumps({"jsonrpc": "2.0","id": "dontcare","method": "validators","params": [None]})
    curr_validators = requests.request("POST", RPC_URL, headers=headers, data=payload).json()['result']['current_validators']
    val_info = next(v for v in curr_validators if v["account_id"] == validator_id)
    res_dict['stake'] = val_info['stake']
    res_dict['num_expected_blocks'] = val_info['num_expected_blocks']
    res_dict['num_expected_chunks'] = val_info['num_expected_chunks']
    res_dict['num_produced_blocks'] = val_info['num_produced_blocks']
    res_dict['num_produced_chunks'] = val_info['num_produced_chunks']
    return res_dict