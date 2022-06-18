from max.client import Client
from os.path import exists
import ast


class Grid:
    def __init__(self,key,screct,pair='usdttwd',earn_type='twd'):
        self.client = Client(key, screct)
        vip_level = self.client.get_private_vip_level()
        self.maker_fee = vip_level['current_vip_level']['maker_fee']
        self.taker_fee = vip_level['current_vip_level']['taker_fee']
        self.pair = pair
        self.all_price_list = {}
        self.init_info = {'balance':0,'price':0,'amount':0}
        self.new_info = {'balance':0,'price':0,'amount':0}
        self.grade = 0
        self.realized_profit = 0
        self.floating_profit = 0
        self.earn_type = earn_type
        self.max_pending_orders = {}
        self.grid_path = 'grid_parameter.txt'
        self.grid_exists()

    def grid_exists(self):
        if exists(self.grid_path):
            with open(self.grid_path) as f:
                self.all_price_list = ast.literal_eval(f.readline())
                self.init_info =  ast.literal_eval(f.readline())
                self.new_info =  ast.literal_eval(f.readline())
                self.grade =  ast.literal_eval(f.readline())
                self.pair =  ast.literal_eval(f.readline())
                self.earn_type =  ast.literal_eval(f.readline())
                self.realized_profit =  ast.literal_eval(f.readline())
            self.max_pending_orders = self.all_price_list


    def get_base_info(self):
        #get available balance
        ava_balance = {'USDT':self.client.get_private_account_balance('USDT'),
                    'TWD':self.client.get_private_account_balance('TWD')}
        return ava_balance

    def cancel_all_orders(self,sell_all=False):
        self.client.set_private_cancel_orders(self.pair,'sell')
        self.client.set_private_cancel_orders(self.pair,'buy')
        if sell_all:
            newprice = self.get_market_price()
            self.client.set_private_create_order(
                    pair=self.pair,
                    side='sell',
                    amount=round(float(self.new_info['amount']),2),
                    price=newprice['buy']
                )

    def get_market_price(self):
        # get market price
        res = self.client.get_public_all_tickers(self.pair)
        return {'buy':res['buy'],'sell':res['sell']}

    def count_grade_profit(self,upper,lower,grid_num):
        self.grade = round((upper - lower) / (grid_num-1),3)
        profit_range = {
            'min': round(((self.grade/upper) - self.maker_fee)*100,2),
            'max': round(((self.grade/lower) - self.maker_fee)*100,2)}
        self.init_info['price'] = float(self.get_market_price()['sell'])
        self.least = grid_num*9*self.init_info['price'] if self.earn_type=='TWD' else grid_num*9*upper
        self.least = round(self.least*1.003)
        return {'grade':self.grade,'profit':profit_range,'least':self.least}

    def create_all_price_list(self,upper,lower,grid_num,order_amount):
        self.init_info['balance'] = order_amount
        if order_amount < self.least:
            return False
        self.init_info['price'] = float(self.get_market_price()['sell'])
        grid_per_amount = self.init_info['balance'] / (grid_num-1)
        self.cancel_all_orders()

        for i in range(grid_num):
            price = round(lower+(self.grade*i),3) if i != (grid_num-1) else upper
            self.all_price_list[i] = {'price':price,
                                      'amount':0,
                                      'side':'N',
                                      'orderId':-1}
            
            placeNum = round(grid_per_amount/self.init_info['price'],2) if self.earn_type == 'TWD' else round(grid_per_amount/price,2)
            self.all_price_list[i]['amount'] = placeNum

            if price <= self.init_info['price'] and (self.init_info['price'] - price) > self.grade/2:
                self.all_price_list[i]['side'] = 'buy'
            if price >= self.init_info['price'] and (price - self.init_info['price']) > self.grade/2:
                self.all_price_list[i]['side'] = 'sell'
                self.init_info['amount'] += grid_per_amount/self.init_info['price']

        self.init_info['amount']=round(self.init_info['amount'],2)
        return True

    def place_order(self):
        try:
            self.client.set_private_create_order(
                pair=self.pair,
                side='buy',
                amount=self.init_info['amount'],
                price=self.init_info['price']
            )
            for i,item in self.all_price_list.items():
                if item['side'] == 'N':
                    continue
                self.all_price_list[i]['orderId'] = self.client.set_private_create_order(
                    pair=self.pair,
                    side=item['side'],
                    amount=item['amount'],
                    price=item['price']
                )['id']
            self.max_pending_orders = self.all_price_list
            self.new_info['amount'] = self.init_info['amount']
            self.new_info['price']=self.init_info['price']
            self.new_info['balance'] = self.init_info['balance']-(self.init_info['amount']*self.init_info['price'])
            self._record()
            return 'done'
        except Exception as e:
            return str(e)

    def checking_orders(self):
        for i,item in self.all_price_list.items():
            if item['orderId'] != -1:
                continue
            pre = i-1 if i>0 else i
            nex = i+1 if i<len(self.all_price_list)-1 else i
            
            order_info = self.client.get_private_order_detail(item['orderId'])
            if order_info['state']=='done':
                if order_info['side']=='buy':
                    self.max_pending_orders[nex]['side']='sell'
                    self.new_info['amount'] += item['amount']
                    self.new_info['balance'] -= item['amount']*item['price']
                elif order_info['side']=='sell':
                    self.max_pending_orders[pre]['side']='buy'
                    self.new_info['amount'] -= item['amount']
                    self.new_info['balance'] += item['amount']*item['price']
                    if self.earn_type=='TWD':
                        self.realized_profit += self.grade*item['amount']  
                    else: 
                        self.realized_profit += self.max_pending_orders[i]['amount'] - self.max_pending_orders[pre]['amount']

                self.max_pending_orders[nex]['orderId'] = self.client.set_private_create_order(
                    pair=self.pair,
                    side=self.max_pending_orders[nex]['side'],
                    amount=self.max_pending_orders[nex]['amount'],
                    price=self.max_pending_orders[nex]['price']
                )['id']
        
        self.all_price_list=self.max_pending_orders
        newPrice = self.get_market_price()
        self.new_info['price']=newPrice['buy']
        if self.earn_type == 'TWD':
            self.floating_profit = round((self.realized_profit / self.init_info['balance'])*100,2)
        else:
            self.floating_profit = round((self.realized_profit / self.init_info['amount'])*100,2)


    def _record(self):
        with open(self.grid_path,'w') as f:
            f.write(str(self.all_price_list)+'\n')
            f.write(str(self.init_info)+'\n')
            f.write(str(self.new_info)+'\n')
            f.write(str(self.grade)+'\n')
            f.write(str(self.pair)+'\n')
            f.write(str(self.earn_type)+'\n')
            f.write(str(self.realized_profit))














### never using this code! count rate only
# elif grade_or_rate == 'rate':
#     x = sp.Symbol('x')
#     rate = sp.solve(lower * (1+x)**(grid_num-1) - upper)
#     for i in rate:
#         try:
#             print(eval(str(sp.N(i))))
#         except:
#             continue