from helpers import *

t = time.time()
RELEVANT_VALIDATORS = json.load(open("RELEVANT_VALIDATORS.json"))

base_dir_path = os.path.dirname(os.path.realpath(__file__))
data_dir_path = os.path.join(base_dir_path, 'data')
blocks_csv_path = os.path.join(data_dir_path, 'blocks_recorded.csv')
historical_csv_path = os.path.join(data_dir_path, 'back_populated.csv')
historical_df = pd.read_csv(historical_csv_path)


blocks_df = pd.read_csv(blocks_csv_path)

# Update blocks_recorded csv
curr_block_details = get_block_details(81086098)
print(bcolors.OKBLUE, "Current block height:", curr_block_details['block_height'], bcolors.ENDC)

# if last block's epoch ID in blocks_recorded.csv is not the same as current block's epoch ID, then need to add new epoch to historical.csv
last_recorded_block = blocks_df[blocks_df['block_height'] == 81032074].iloc[0]
new_row = {}

# Retrieve all relevant values from the last block in blocks_recorded.csv
for key in last_recorded_block.keys():
    new_row[key] = last_recorded_block[key]
del new_row['block_height']
print(new_row)

start_block = int(get_block_details(last_recorded_block['prev_epoch_last_block'])['block_height']) + 1
new_row['start_block'] = start_block
new_row['end_block'] = start_block+43200
new_row['block_time_empirical'] = get_avg_block_time_for_epoch(start_block)
validators_info = get_ALL_validators_info(block_num=start_block+43200-1)

tries = 0
for i, addr in enumerate(RELEVANT_VALIDATORS):
    # try:
        print(addr)
        rew_res = get_rewards_for_epoch(addr,new_row['start_block'], new_row['end_block'])
        added_stake = int(get_recent_stake_txns_for_validator(addr, new_row['start_block'], new_row['end_block'])[1])

        new_row[f'val_{i}_name'] =  addr
        new_row[f'val_{i}_expected_blocks'] =  validators_info[addr]['expected_blocks']
        new_row[f'val_{i}_produced_blocks'] =  validators_info[addr]['produced_blocks']
        new_row[f'val_{i}_expected_chunks'] =  validators_info[addr]['expected_blocks']
        new_row[f'val_{i}_produced_chunks'] =  validators_info[addr]['produced_blocks']
        new_row[f'val_{i}_is_slashed'] =  int(validators_info[addr]['is_slashed'])
        new_row[f'val_{i}_sum_stake'] =  int(validators_info[addr]['stake'])
        new_row[f'val_{i}_active_stake'] =  int(rew_res[0])
        new_row[f'val_{i}_inactive_stake'] =  int(rew_res[1])
        new_row[f'val_{i}_added_stake'] = added_stake
        new_row[f'val_{i}_stake_diff'] = int(rew_res[2])
        new_row[f'val_{i}_total_rewards'] = int(rew_res[2])-added_stake
        new_row[f'val_{i}_median_rew/stk'] = float(rew_res[3])

        print(bcolors.OKGREEN, "New method", (float(rew_res[2]) - added_stake)/float(rew_res[0]-added_stake)*640*100, "% APY", bcolors.ENDC)
        print(new_row)
        print()
        time.sleep(0.2)
        tries = 0
    # except:
    #     tries += 1
    #     if tries > 5:
    #         exit()
    #     print(bcolors.FAIL, addr, " failed", bcolors.ENDC)
historical_df = pd.concat( [historical_df, pd.DataFrame([new_row])], ignore_index=True)
historical_df.to_csv(historical_csv_path, index=False)