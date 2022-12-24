from helpers import *

dir_path = 'data/all_stakes/epoch-1656.json'
temp = get_ALL_validators_info(None)
json.dump(temp, open(dir_path, 'w'))