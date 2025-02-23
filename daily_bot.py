from global_import import *
import matplotlib.pyplot as plt
import seaborn as sns
from slack import WebClient
from datetime import date

TEST_SLACK_UPLOAD_TOKEN = os.getenv("TEST_SLACK_UPLOAD_TOKEN")
TEST_SLACK_CHANNEL_ID = os.getenv("TEST_SLACK_CHANNEL_ID")


def get_historical_dataframe():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    historical_df = pd.read_csv(f"{base_dir}/data/val_out.csv")
    max_epoch_height = historical_df['Epoch Number'].max()
    historical_df = historical_df[historical_df['Epoch Number'] > (max_epoch_height - 12)]
    return historical_df

def get_24hrs_rewards_and_stake():
    df = get_historical_dataframe()
    rewards = df[df['Validator Name'] == 'twinstake.poolv1.near'][-2:]['Actual Rewards'].sum()
    stake = df[df['Validator Name'] == 'twinstake.poolv1.near']['Stake'].iloc[-1]
    apy = df[df['Validator Name'] == 'twinstake.poolv1.near']['Realized APY'].iloc[-2:].mean()
    return rewards, stake, apy

def generate_chart():
    df = get_historical_dataframe()
    
    charting_df = pd.DataFrame()
    charting_df.index = df['Epoch Number'].unique()
    charting_df['Twinstake APY'] = list(df[df['Validator Name'] == 'twinstake.poolv1.near']['Realized APY'])
    charting_df.loc[charting_df['Twinstake APY'] > 15, 'Twinstake APY'] = np.nan

    ls = [i for i in df[df['Block Producer'] == 1].groupby('Epoch Number')['Realized APY'].median() - df[df['Block Producer'] == 0].groupby('Epoch Number')['Realized APY'].median() if np.abs(i) > 0.02]
    if len(ls) > 0:
        charting_df['Blocks Producers APY (Median)'] = df[df['Block Producer'] == 1].groupby('Epoch Number')['Realized APY'].median()
        charting_df['Chunk Producers APY (Median)'] = df[df['Block Producer'] == 0].groupby('Epoch Number')['Realized APY'].median()
        
    charting_df['Largest Stakers APY (Median)'] = df[df['Block Producer'] == 1].groupby('Epoch Number')['Realized APY'].median()
    charting_df.loc[charting_df['Largest Stakers APY (Median)'] > 15, 'Largest Stakers APY (Median)'] = np.nan

    # Plot the chart
    plt.cla() # Clear the plot from previous chain charts (if any)
    ax = sns.lineplot(data=charting_df, markers=True)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right")
    ax.set_ylabel('APY (%)')
    ax.set_ylim([10,12])
    ax.set_title(f"NEAR Staking APY (Last 12 Epochs)")

    # Add the APY values to the chart
    for ind, row in charting_df.iterrows():
        ax.text(ind-0.5, row['Twinstake APY']+0.05, str(round(float(row['Twinstake APY']),2)))

    # Plot the delta APY for TS vs Avg
    delta_apy = abs(round(charting_df['Twinstake APY'] - charting_df['Largest Stakers APY (Median)'],2))
    ax2 = ax.twinx()
    ax2.plot(delta_apy, color='blue')
    ax2.tick_params(axis='y', labelcolor='blue')
    ax2.set_ylim([0.005,2])
    ax2.set_ylabel('Absolute Difference in APY (TS vs Avg)')

    # Save the chart to a file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    chart_path = f"{base_dir}/data/chart.png"
    ax.figure.savefig(chart_path, bbox_inches='tight')

def send_chart_to_channel(_rewards, _stake, _apy):
    slack_message = f'---------------------------------\n'
    slack_message += f'*Historical performance of TwinStake validator on Near* \n'
    slack_message += f'Rewards earned in last 2 epochs (~27 hours): {round(_rewards,2)} NEAR \n'
    slack_message += f'AUD: {int(_stake)} NEAR \n'
    slack_message += f'APY: {round(_apy, 2)} % \n'

    client = WebClient(TEST_SLACK_UPLOAD_TOKEN)
    chart_path = os.path.dirname(__file__) + '/data/chart.png'
    img = open(chart_path, 'rb').read()

    response = client.files_upload(
        channels = TEST_SLACK_CHANNEL_ID,
        initial_comment = slack_message,
        filename = f"DailyChart-{date.today()}",
        content = img
    )
    # For optimisation need to upload file, collect the permalink and then send the message embedding the image
    print("Permalink:", response['file']['permalink'])

def daily_bot_send_chart():
    rewards, stake, apy = get_24hrs_rewards_and_stake()
    generate_chart()
    send_chart_to_channel(rewards, stake, apy)

if __name__ == "__main__":
    daily_bot_send_chart()