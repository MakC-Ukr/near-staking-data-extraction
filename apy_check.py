from helpers import *

if __name__ == '__main__':
    start_block = 80495491
    RELEVANT_VALIDATORS = json.load(open("RELEVANT_VALIDATORS.json"))
    RELEVANT_VALIDATORS[14] = 'twinstake.poolv1.near'
    validators_info = get_ALL_validators_info(block_num=start_block+43200-1)
    df_ls = []
    for i, addr in enumerate(RELEVANT_VALIDATORS[:15]):
        new_row = {}
        before_info = get_acc_info_for_block(addr, start_block) # Assuming these blocks exist
        after_info = get_acc_info_for_block(addr, start_block+43200)
        new_row[f'val_name'] =  addr
        new_row[f'val_expected_blocks'] =  validators_info[addr]['expected_blocks']
        new_row[f'val_produced_blocks'] =  validators_info[addr]['produced_blocks']
        new_row[f'val_expected_chunks'] =  validators_info[addr]['expected_blocks']
        new_row[f'val_produced_chunks'] =  validators_info[addr]['produced_blocks']
        new_row[f'val_is_slashed'] =  int(validators_info[addr]['is_slashed'])
        new_row[f'val_stake'] =  validators_info[addr]['stake']
        new_row[f'val_initial_amount'] =  float(before_info['amount'])
        new_row[f'val_initial_locked'] =  float(before_info['locked'])
        new_row[f'val_final_amount'] =  float(after_info['amount'])
        new_row[f'val_final_locked'] =  float(after_info['locked'])
        time.sleep(0.2)
        df_ls.append(new_row)
        print(addr)

    df = pd.DataFrame(df_ls)
    df.to_csv('apy_check.csv', index=False)