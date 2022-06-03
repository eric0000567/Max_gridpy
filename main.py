from time import time
from grid import Grid
from max.client import Client
import sympy as sp
import requests

dataURL = 'https://script.google.com/macros/s/AKfycbwBCAOlZvtzGFG8ZVeA0qHGxaqO1dXCSo-A0V_t_UVAE1pVbEO_LZEL-Rx4wwTTpYi2/exec'
r = requests.get(dataURL)
data = r.json()[0]['data']

upper :float = 35
lower :float = 25
grade :int = 55
earn_type = 'twd'
grid_balance = 10000
grade_or_rate = {'g':'grade','r':'rate'}
pair :str = 'usdttwd'

gd = Grid('JowUYDqT6GplbBt0CAgsIUx0ZNskN899EXnmxTYe', 'jve7dZ2CEElLAGxNAXeLx5RANwaon9FdpFn4239a')

def main():
    '''
    0.get user balance
    1.setting grid parameter
    2.count profit
    3.create all price list and buy/sell dict
    4.enter TWD or USDT balance
    5.check enough balance and more than least limit
    6.place orders and record init balance 
    7.checking orders 
    '''
    init_balance = gd.get_base_info('usdt','twd')
    print(init_balance)
    ans = gd.count_grade_profit(upper,lower,grade)
    grade_list = gd.create_all_price_list(upper,lower,grade)
    print(ans)
    gd.create_buysell_list()
    create_orders = gd.create_init_order(grid_balance)
    if create_orders:
        print('succes')
    else:
        print('fail, your balance is not enough')
        return False
    while True:
        time.sleep(90)
        # use mp.process
        gd.checking_orders()





