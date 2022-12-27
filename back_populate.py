from helpers import *

base_dir_path = os.path.dirname(os.path.realpath(__file__))
data_dir_path = os.path.join(base_dir_path, 'data')
blocks_csv_path = os.path.join(data_dir_path, 'blocks_recorded.csv')
blocks_df = pd.read_csv(blocks_csv_path)

historical_csv_path = os.path.join(data_dir_path, 'back_populated.csv')
historical_df = pd.read_csv(historical_csv_path)

# get all rows from blocks_df where epoch_id is not in historical_df 
blocks_df = blocks_df[~blocks_df['epoch_id'].isin(historical_df['epoch_id'])]
blocks_df.reset_index(drop=True, inplace=True)

#delete rows from blocks_df which have duplicate epoch_id
blocks_df = blocks_df.drop_duplicates(subset=['epoch_id'], keep='first')
print(blocks_df)

for i in tqdm(range(len(blocks_df)-1)):
    BLOCK_FROM_RECORDED_BLOCKS_DF = int(blocks_df.iloc[i]['block_height'])
    ANY_BLOCK_FROM_EPOCH = int(blocks_df.iloc[i+1]['block_height'])

    t = time.time()
    RELEVANT_VALIDATORS = json.load(open("RELEVANT_VALIDATORS.json"))

    curr_block_details = get_block_details(ANY_BLOCK_FROM_EPOCH)
    print(bcolors.OKBLUE, "Current block height:", curr_block_details['block_height'], bcolors.ENDC)
    last_recorded_block = blocks_df[blocks_df['block_height'] == BLOCK_FROM_RECORDED_BLOCKS_DF].iloc[0]
    new_row = {}
    for key in last_recorded_block.keys():
        new_row[key] = last_recorded_block[key]
    del new_row['block_height']
    
    start_block = int(get_block_details(last_recorded_block['prev_epoch_last_block'])['block_height']) + 1
    new_row['epoch_height'] = int((start_block-last_recorded_block['GENESIS_HEIGHT'])//43200)
    new_row['start_block'] = start_block
    new_row['end_block'] = start_block+43200
    new_row['block_time_empirical'] = get_avg_block_time_for_epoch(start_block)
    validators_info = get_ALL_validators_info(block_num=start_block+43200-1)

    tries = 0
    for i, addr in enumerate(RELEVANT_VALIDATORS):
        new_row[f'val_{i}_name'] =  addr
        try:
            print(addr)
            change_in_stake = get_rewards_for_epoch(addr,new_row['start_block'], new_row['end_block'])
            added_stake = int(get_recent_stake_txns_for_validator(addr, new_row['start_block'], new_row['end_block'])[1])
            rewards_v2 = int(get_rewards_v2(addr, new_row['start_block'], new_row['end_block']))

            new_row[f'val_{i}_expected_blocks'] =  validators_info[addr]['expected_blocks']
            new_row[f'val_{i}_produced_blocks'] =  validators_info[addr]['produced_blocks']
            new_row[f'val_{i}_expected_chunks'] =  validators_info[addr]['expected_blocks']
            new_row[f'val_{i}_produced_chunks'] =  validators_info[addr]['produced_blocks']
            new_row[f'val_{i}_is_slashed'] =  int(validators_info[addr]['is_slashed'])
            new_row[f'val_{i}_sum_stake'] =  int(validators_info[addr]['stake'])
            new_row[f'val_{i}_active_stake'] =  int(change_in_stake[0])
            new_row[f'val_{i}_added_stake'] = added_stake
            new_row[f'val_{i}_stake_diff'] = int(change_in_stake[1])
            new_row[f'val_{i}_total_rewards'] = int(change_in_stake[1])-added_stake
            new_row[f'val_{i}_median_rew/stk'] = float(change_in_stake[2])
            new_row[f'val_{i}_commission'] = get_validator_commission(addr, new_row['end_block'])
            new_row[f'val_{i}_total_rewards_v2'] = rewards_v2

            # print(bcolors.OKGREEN, "New method", (float(chaçnge_in_stake[1]) - added_stake)/float(change_in_stake[0]-added_stake)*640*100, "% APY", bcolors.ENDC)
            # print(new_row)
            print()
            time.sleep(0.2)
            tries = 0
        except:
            tries += 1
            if tries > 5:
                exit()
            print(bcolors.FAIL, addr, " failed", bcolors.ENDC)
            time.sleep(30)
    historical_df = pd.concat( [historical_df, pd.DataFrame([new_row])], ignore_index=True)
    historical_df.to_csv(historical_csv_path, index=False)

    print(bcolors.OKGREEN, "Time taken:", time.time()-t, bcolors.ENDC)