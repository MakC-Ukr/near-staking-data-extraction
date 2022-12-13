from helpers import *


RELEVANT_VALIDATORS = json.load(open("RELEVANT_VALIDATORS.json"))

base_dir_path = os.path.dirname(os.path.realpath(__file__))
data_dir_path = os.path.join(base_dir_path, 'data')
historical_csv_path = os.path.join(data_dir_path, 'near_historical.csv')
blocks_csv_path = os.path.join(data_dir_path, 'blocks_recorded.csv')

historical_df = pd.read_csv(historical_csv_path)
blocks_df = pd.read_csv(blocks_csv_path)

# Update blocks_recorded csv
curr_block_details = get_block_details()

# if last block's epoch ID in blocks_recorded.csv is not the same as current block's epoch ID, then need to add new epoch to historical.csv
if len(blocks_df) > 0 and curr_block_details['epoch_id'] != blocks_df.iloc[-1]['epoch_id']:
    print(bcolors.OKGREEN, "New epoch detected. Updating historical.csv", bcolors.ENDC)
    last_recorded_block = blocks_df.iloc[-1]
    new_row = {}

    # Retrieve all relevant values from the last block in blocks_recorded.csv
    for key in last_recorded_block.keys():
        new_row[key] = last_recorded_block[key]
    del new_row['block_height']

    start_block = int(last_recorded_block['epoch_start_height'])
    new_row['start_block'] = start_block
    new_row['end_block'] = start_block+43200
    new_row['block_time_empirical'] = TEST_get_avg_block_time_for_epoch(start_block)
    validators_info = get_ALL_validators_info(block_num=start_block+43200-1)

    for i, addr in enumerate(RELEVANT_VALIDATORS):
        before_info = get_acc_info_for_block(addr, start_block) # Assuming these blocks exist
        after_info = get_acc_info_for_block(addr, start_block+43200)
        new_row[f'val_{i}_name'] =  addr
        new_row[f'val_{i}_expected_blocks'] =  validators_info[addr]['expected_blocks']
        new_row[f'val_{i}_produced_blocks'] =  validators_info[addr]['produced_blocks']
        new_row[f'val_{i}_expected_chunks'] =  validators_info[addr]['expected_blocks']
        new_row[f'val_{i}_produced_chunks'] =  validators_info[addr]['produced_blocks']
        new_row[f'val_{i}_is_slashed'] =  int(validators_info[addr]['is_slashed'])
        new_row[f'val_{i}_stake'] =  validators_info[addr]['stake']
        new_row[f'val_{i}_initial_amount'] =  float(before_info['amount'])
        new_row[f'val_{i}_initial_locked'] =  float(before_info['locked'])
        new_row[f'val_{i}_final_amount'] =  float(after_info['amount'])
        new_row[f'val_{i}_final_locked'] =  float(after_info['locked'])
        time.sleep(0.2)
    historical_df = pd.concat( [historical_df, pd.DataFrame([new_row])], ignore_index=True)
    historical_df.to_csv(historical_csv_path, index=False)
    
# No new epoch detected. Record latest block in blocks_recorded.csv
new_row = {}
constant_vals = get_constant_vals()
for key in constant_vals:
    new_row[key] = constant_vals[key]
for key in curr_block_details:
    new_row[key] = curr_block_details[key]
new_row['epoch_start_height'] = int(80495491)
new_row['total_staked'] = get_total_stake()
blocks_df = pd.concat( [blocks_df, pd.DataFrame([new_row])], ignore_index=True)
blocks_df.to_csv(blocks_csv_path, index=False)