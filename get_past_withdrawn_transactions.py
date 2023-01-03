from helpers import *

RELEVANT_VALIDATORS = json.load(open("RELEVANT_VALIDATORS.json"))

df = pd.read_csv("data/near_historical.csv")
df = df[-5:-4]
epochs = list(df["epoch_height"])
starts = list(df['start_block'])
ends = list(df['end_block'])
print(epochs)

for epoch_ind, epoch_height in enumerate(epochs):
    for val_ind, val in enumerate(RELEVANT_VALIDATORS):
        amt = get_recent_UNSTAKE_txns_for_validator(val, starts[epoch_ind], ends[epoch_ind])
        print(f"Validator {val} in epoch {epoch_height} unstaked amount: {amt} ")
        df.loc[df['epoch_height'] == epoch_height, f'val_{val_ind}_unstaked_amount'] = amt
        df.to_csv("data/near_historical_withdrawn.csv", index=False)

df.to_csv("data/near_historical_withdrawn.csv", index=False)