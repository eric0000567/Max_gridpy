from time import time
from LoginPage import *
from tkinter import *
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
root = Tk()
root.title('MAX匯率網格')
LoginPage(root)
# root.mainloop()
# with mp.Pool(4) as p:
    # result1 = p.map(root.mainloop(), chunksize=100000)
target=root.mainloop()






