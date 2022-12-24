import random
import time
import numpy as np
import os
import requests
import pandas as pd
from dotenv import load_dotenv
import json
from tqdm import tqdm

class bcolors:
    WARNING = '\033[93m'
    ENDC = '\033[0m'
    OKBLUE = '\033[94m'
    FAIL = '\033[91m'

load_dotenv()
RPC_URL = os.getenv("RPC_URL")
RPC_URL_PUBLIC = os.getenv("RPC_URL_PUBLIC")
RPC_URL_PUBLIC_ARCHIVAL = os.getenv("RPC_URL_PUBLIC_ARCHIVAL")
NEAR_BLOCKS_API = 'https://api.nearblocks.io/v1/'

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

headers = {'Content-Type': 'application/json'}