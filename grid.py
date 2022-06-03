from tenacity import retry, retry_unless_exception_type
from max.client import Client
import sympy as sp

class Grid:
    def __init__(self,key,secret,pair='usdttwd',earn_type='twd') :
        self.client = Client(key, secret)
        self.vip_level = self.client.get_private_vip_level()
        self.maker_fee = self.vip_level['current_vip_level']['maker_fee']
        self.taker_fee = self.vip_level['current_vip_level']['taker_fee']
        self.pair = pair
        self.all_price_list = []
        self.buy_dict = {}
        self.sell_dict = {}
        self.init_info = {'balance':0,'price':0,'amount':0}
        self.grid_per_amount = 0
        self.grade = 0
        self.realized_profit = 0
        self.floating_profit = 0
        self.least_money=0
        self.earn_type = earn_type
        self.max_pending_orders = {}

    def get_base_info(self,Acrypto='USDT',Bcrypto='TWD'):
        #get available balance
        ava_balance = {Acrypto:self.client.get_private_account_balance(Acrypto),
                    Bcrypto:self.client.get_private_account_balance(Bcrypto)}
        return ava_balance

    def cancel_all_orders(self,sell_self=False):
        self.client.set_private_cancel_orders(self.pair,'sell')
        self.client.set_private_cancel_orders(self.pair,'buy')
        if not sell_self:
            self.client.set_private_create_order(
                    pair=self.pair,
                    side='sell',
                    amount=round(self.get_base_info('USDT')['USDT']['balance'],2),
                    _type='market'
                )

    def get_market_price(self):
        # get market price
        res = self.client.get_public_all_tickers(self.pair)
        return {'buy':res['buy'],'sell':res['sell']}

    def count_grade_profit(self,upper,lower,grid_num):
        self.grade = round((upper - lower) / (grid_num-1),3)
        self.least_money = grid_num*9
        profit_range = {
            'min': round((self.grade/upper) - self.maker_fee,4),
            'max': round((self.grade/lower) - self.maker_fee,4)}
        return {'grade':self.grade,'profit':profit_range}

    def create_all_price_list(self,upper,lower,grid_num):
        self.all_price_list = [round(lower+(self.grade*i),3) for i in range(grid_num)]
        self.all_price_list[-1] = upper
        return self.all_price_list

    def create_buysell_list(self):
        self.init_info['price'] = float(self.get_market_price()['sell'])
        for price in self.all_price_list:
            self.buy_dict[price] = None
            self.sell_dict[price] = None

            if price <= self.init_info['price'] and (self.init_info['price'] - price) > self.grade/2:
                self.buy_dict[price] = price
            if price >= self.init_info['price'] and (price - self.init_info['price']) > self.grade/2:
                self.sell_dict[price] = price

    def create_init_order(self,order_amount):
        if order_amount < self.least_money:
            return False
        self.cancel_all_orders()
        self.init_info['balance'] = round(order_amount*0.997,2)
        self.create_buysell_list()
        self.grid_per_amount = self.init_info['balance'] / len(self.all_price_list)
        if self.earn_type == 'twd':
            self.grid_per_amount /= self.init_info['price']

        # buy init sell amount
        buy_amount = 0
        for i in self.sell_dict:
            if i is not None:
                buy_amount+=1
        self.init_info['amount'] = round(self.grid_per_amount/self.init_info['price'],2)*buy_amount 
        self.client.set_private_create_order(
                pair=self.pair,
                side='buy',
                amount=self.init_info['amount'],
                price=price,
                _type='market'
            )

        #pending orders
        for price,order in self.buy_dict.items():
            if order is not None:
                self.buy_dict[price] = self.client.set_private_create_order(
                    pair=self.pair,
                    side='buy',
                    amount=round(self.grid_per_amount,2) if self.earn_type == 'twd' else round(self.grid_per_amount/price,2),
                    price=price,
                    _type='limit'
                )
        for price,order in self.sell_dict.items():
            if order is not None:
                self.sell_dict[price] = self.client.set_private_create_order(
                    pair=self.pair,
                    side='sell',
                    amount=round(self.grid_per_amount,2) if self.earn_type == 'twd' else round(self.grid_per_amount/price,2),
                    price=price,
                    _type='limit'
                )
        return True

    def checking_orders(self):
        new_price = self.get_market_price()
        balance = self.get_base_info()
        self.floating_profit = (balance['USDT']*new_price['buy'] + self.realized_profit) - self.init_info['balance']
        for price in self.all_price_list:
            if self.buy_dict[price] is not None:
                order_state = self.client.get_private_order_detail(self.buy_dict[price]['client_id'])['state']
                if order_state == 'done':
                    self.buy_dict[price] = None
                    p = price+self.grade
                    self.sell_dict[p] = self.client.set_private_create_order(
                        pair=self.pair,
                        side='sell',
                        amount=round(self.grid_per_amount,2) if self.earn_type == 'twd' else round(self.grid_per_amount/p,2),
                        price=p,
                        _type='limit'
                    )
            if self.sell_dict[price] is not None:
                order_state = self.client.get_private_order_detail(self.sell_dict[price]['client_id'])['state']
                if order_state == 'done':
                    self.sell_dict[price] = None
                    self.realized_profit += self.grade
                    p = price-self.grade
                    self.buy_dict[p] = self.client.set_private_create_order(
                        pair=self.pair,
                        side='buy',
                        amount=round(self.grid_per_amount,2) if self.earn_type == 'twd' else round(self.grid_per_amount/p,2),
                        price=p,
                        _type='limit'
                    )
                
   









### never using this code! count rate only
# elif grade_or_rate == 'rate':
#     x = sp.Symbol('x')
#     rate = sp.solve(lower * (1+x)**(grid_num-1) - upper)
#     for i in rate:
#         try:
#             print(eval(str(sp.N(i))))
#         except:
#             continue