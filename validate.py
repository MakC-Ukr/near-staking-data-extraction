import math
import os
import numpy as np
import pandas as pd
import time
import datetime

No_Validators = 26

def validate_historical_file():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = f"{base_dir}/data/near_historical.csv"
    df_historical= pd.read_csv(path)

    df_historical = df_historical[df_historical['epoch_height'] >= 1660]
    df_historical.reset_index(drop=True, inplace=True)

    df_output = pd.DataFrame(columns = ['Epoch Number', 'Validator Name', 'Stake', 'blocks_prod_ratio', 'chunks_prod_ratio','UptimePCT', 'Uptime', 'Actual Rewards', 'Expected Rewards', 'Realized APY', 'Expected APY', 'Absolute Difference in Rewards', 'Absolute Difference in APY', '% Difference in Rewards', 'Rewards Method Used'],
                            index = range(No_Validators))
    df_outputHist = pd.DataFrame(columns = ['Epoch Number', 'Validator Name', 'Stake', 'blocks_prod_ratio', 'chunks_prod_ratio','UptimePCT', 'Uptime', 'Actual Rewards', 'Expected Rewards', 'Realized APY', 'Expected APY',
                                            'Absolute Difference in Rewards', 'Absolute Difference in APY', '% Difference in Rewards'])

    for row in range (2, len(df_historical)):
    # Constants from Network
        totalStake                          = float(df_historical['total_staked'][row-2])*1E-24
        totalSupply                         = float(df_historical['total_supply'][row-2])*1E-24
        Block_time_empirical                = float(df_historical['block_time_empirical'][row-2]) 
        ONLINE_THRESHOLD_MIN                = float(df_historical['ONLINE_THRESHOLD_MIN'][row])
        ONLINE_THRESHOLD_MAX                = float(df_historical['ONLINE_THRESHOLD_MAX'][row])   
        TREASURY_PCT                        = 0.1
        EPOCHS_PER_YEAR                     = float(df_historical['EPOCHS_A_YEAR'][row])
        EPOCH_LENGTH                        = float(df_historical['EPOCH_LENGTH'][row])
        REWARD_PCT_PER_YEAR                 = 0.05
        BLOCK_PRODUCER_KICKOUT_THRESHOLD    = float(df_historical['BLOCK_PRODUCER_KICKOUT_THRESHOLD'][row])
        CHUNK_PRODUCER_KICKOUT_THRESHOLD    = float(df_historical['CHUNK_PRODUCER_KICKOUT_THRESHOLD'][row])
        E_blockTime                         = float(df_historical['BLOCK_TIME_TARGET'][row])


    # Parameters to be varied by validator
        for i in range(No_Validators):
            df_output['Validator Name'][i]                   = df_historical[f'val_{i}_name'][row]
            df_output['Epoch Number'][i]                     = df_historical['epoch_height'][row]   
            df_output['Stake'][i]                            = float(df_historical[f'val_{i}_sum_stake'][row-2])*1E-24

            num_produced_blocks                = float(df_historical[f'val_{i}_produced_blocks'][row-2])
            num_expected_blocks                = float(df_historical[f'val_{i}_expected_blocks'][row-2])
            num_produced_chunks                = float(df_historical[f'val_{i}_produced_chunks'][row-2])
            num_expected_chunks                = float(df_historical[f'val_{i}_expected_chunks'][row-2])

            if num_expected_blocks == 0 and num_expected_chunks == 0:
                uptime_Pct_v = 0
                blocks_prod_ratio = 0
                chunks_prod_ratio = 0
            elif num_expected_blocks == 0:
                if num_produced_chunks/num_expected_chunks < CHUNK_PRODUCER_KICKOUT_THRESHOLD/100:
                    uptime_Pct_v = 0
                    blocks_prod_ratio = 0
                    chunks_prod_ratio = num_produced_chunks/num_expected_chunks
                else:  
                    uptime_Pct_v = num_produced_chunks/num_expected_chunks
                    blocks_prod_ratio = 0
                    chunks_prod_ratio = num_produced_chunks/num_expected_chunks
            elif num_produced_blocks/num_expected_blocks < BLOCK_PRODUCER_KICKOUT_THRESHOLD/100 or num_produced_chunks/num_expected_chunks < CHUNK_PRODUCER_KICKOUT_THRESHOLD/100:
                uptime_Pct_v = 0
                blocks_prod_ratio = num_produced_blocks/num_expected_blocks
                chunks_prod_ratio = num_produced_chunks/num_expected_chunks
            else:
                uptime_Pct_v = (num_produced_blocks/num_expected_blocks + num_produced_chunks/num_expected_chunks)/2
                blocks_prod_ratio = num_produced_blocks/num_expected_blocks
                chunks_prod_ratio = num_produced_chunks/num_expected_chunks

            df_output['blocks_prod_ratio'][i] = blocks_prod_ratio
            df_output['chunks_prod_ratio'][i] = chunks_prod_ratio
            df_output['UptimePCT'][i]         = uptime_Pct_v


            uptime_v                          = min(1,max(0,(uptime_Pct_v-ONLINE_THRESHOLD_MIN) / (ONLINE_THRESHOLD_MAX-ONLINE_THRESHOLD_MIN)))
            df_output['Uptime'][i]            = uptime_v

            E_epochReward           = totalSupply * ( REWARD_PCT_PER_YEAR/EPOCHS_PER_YEAR) *Block_time_empirical/E_blockTime
            E_totalValidatorReward  = (1-TREASURY_PCT)*E_epochReward
            E_validator             = uptime_v * E_totalValidatorReward * df_output['Stake'][i]/totalStake

            E_APY                      = (1+E_validator/df_output['Stake'][i])**(EPOCHS_PER_YEAR*E_blockTime/Block_time_empirical)-1 # POOR MODEL; SHOULD LOOP THROUGH YEAR
                
            unstaked_amount           = float(df_historical[f'val_{i}_unstaked_amount'][row-2])
            added_stake               = float(df_historical[f'val_{i}_added_stake'][row-2])
            stake_diff                = float(df_historical[f'val_{i}_total_rewards_v2'][row])
            actual_rewards            = (stake_diff - ( added_stake - unstaked_amount))/1e24

            Realized_APY              = (1+actual_rewards/df_output['Stake'][i])**(EPOCHS_PER_YEAR*E_blockTime/Block_time_empirical)-1 
            method_used_for_rewards   = 2

            df_output['Actual Rewards'][i]   = actual_rewards 
            df_output['Expected Rewards'][i] = E_validator

            if float(df_output['Actual Rewards'][i]) != 0:
                pct_diff = (E_validator - float(df_output['Actual Rewards'][i])) / float(df_output['Actual Rewards'][i]) *100
                df_output['% Difference in Rewards'][i] = round(pct_diff, 2)
            else:
                df_output['% Difference in Rewards'][i] = 'NaN'

            df_output['Expected APY'][i]                   = E_APY*100
            df_output['Realized APY'][i]                   = Realized_APY*100    
            df_output['Absolute Difference in Rewards'][i] = E_validator - float(df_output['Actual Rewards'][i])
            df_output['Absolute Difference in APY'][i]     = (df_output['Expected APY'][i]  -   df_output['Realized APY'][i])
            df_output['Rewards Method Used'][i]            = method_used_for_rewards
        df_outputHist = df_outputHist.append(df_output, ignore_index = True)
        df_outputHist = df_outputHist.loc[(df_outputHist["Validator Name"] != ' ') & (df_outputHist["Stake"] > 0)] 

    df_outputHist.to_csv(f"{base_dir}/data/val_out.csv", index = False)

def create_historical_gds():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = f"{base_dir}/data/near_historical.csv"
    df_historical= pd.read_csv(path)

    df_historical = df_historical[df_historical['epoch_height'] >= 1660]
    df_historical.reset_index(drop=True, inplace=True)
    normal_cols = list(df_historical.columns[:16])

    df_ls = []
    for ind, row in df_historical.iterrows():
        for val_index in range(No_Validators):
            new_row = {}
            for col in normal_cols:
                new_row[col] = row[col]
                new_row['Validator Address'] = row[f'val_{val_index}_name']

                new_row['Expected Blocks'] = row[f'val_{val_index}_expected_blocks']
                new_row['Produced Blocks'] = row[f'val_{val_index}_produced_blocks']
                new_row['Expected Chunks'] = row[f'val_{val_index}_expected_chunks']
                new_row['Produced Chunks'] = row[f'val_{val_index}_produced_chunks']
                new_row['Is Slashed'] = row[f'val_{val_index}_is_slashed']
                if new_row['Is Slashed'] == 1:
                    print("SLASHED")
            
                try:
                    new_row['Total Stake'] = int(row[f'val_{val_index}_sum_stake'])//1e24
                except:
                    new_row['Total Stake'] = 0
                
                try:
                    new_row['Stake Added in Epoch'] = int(row[f'val_{val_index}_added_stake'])//1e24
                except:
                    new_row['Stake Added in Epoch'] = 0
            
                try:
                    new_row['Stake Removed in Epoch'] = int(row[f'val_{val_index}_unstaked_amount'])//1e24
                except:
                    new_row['Stake Removed in Epoch'] = 0
                
                new_row['Commission'] = row[f'val_{val_index}_commission']
            df_ls.append(new_row)

    path = f"{base_dir}/data/near_historical_gds.csv"

    # Added by Dave. Is the stake condition ok?
    near_historical_gds = pd.DataFrame(df_ls)
    near_historical_gds = near_historical_gds.loc[(near_historical_gds["Validator Address"] != ' ') & (near_historical_gds["Total Stake"] > 0)] 

    pd.DataFrame(near_historical_gds).to_csv(path, index=False)



if __name__ == "__main__":
    validate_historical_file()
    create_historical_gds()