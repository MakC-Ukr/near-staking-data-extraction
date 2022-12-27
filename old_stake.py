from helpers import *


# epoch 1624 last block = 80020290
last_block = 80020290

for i in range(1624,1660):
    print("Epoch: ", i, "Last block in epoch: ", last_block)

    res_dict = {}
    payload = json.dumps({"jsonrpc": "2.0","id": "dontcare","method": "validators","params": [last_block]})
    curr_validators = requests.request("POST", 'https://archival-rpc.mainnet.near.org', headers=headers, data=payload).json()['result']['current_validators']
    for v in curr_validators:
        single_val = {}
        single_val['produced_blocks'] = v['num_produced_blocks']
        single_val['expected_blocks'] = v['num_expected_blocks']
        single_val['produced_chunks'] = v['num_produced_chunks']
        single_val['expected_chunks'] = v['num_expected_chunks']
        single_val['stake'] = v['stake']
        single_val['is_slashed'] = v['is_slashed']
        res_dict[v['account_id']] = single_val

    dir_path = f'data/all_stakes/epoch-{i}.json'
    json.dump(res_dict, open(dir_path, 'w'))
    
    last_block += 43200
    time.sleep(10)