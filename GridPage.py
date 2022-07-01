from tkinter import *
from grid import *
from tkinter.scrolledtext import ScrolledText
from tkinter.messagebox import *
import multiprocessing as mp

class GridPage(object): # 狀態總覽
    def __init__(self, master=None,gd:Grid=None):
        self.root = master
        self.root.geometry('%dx%d' % (600, 400))
        self.gd = gd
        self.sellSelf = StringVar()
        self.selloption = ["不做任何動作", "賣出所有網格持倉"]
        self.sellSelf.set(self.selloption[0])
        self.createPage()

    def createPage(self):
        self.page = Frame(self.root) #建立Frame
        self.page.pack()
        Label(self.page).grid(row=0, stick=W)
        
        Label(self.page, text = '當前資產狀態').grid(row=0, column=0,columnspan=2, stick=EW, pady=10)
        self.balance = Label(self.page, text = '...')
        self.balance.grid(row=1,columnspan=2, stick=EW, pady=5)
        Button(self.page, text='查看網格資訊', command=self.now_profit).grid(row=12, column=0, stick=E)
        Button(self.page, text='查看當前掛單', command=self.grid_list_info).grid(row=12, column=1, stick=W)
        self.msg = ''
        self.st = ScrolledText(self.page,height=10)
        self.st.grid(row=13, columnspan=2, stick=W, pady=5)

        initBalance = self.gd.get_base_info()
        self.balance['text'] = 'TWD: {} \n USDT: {}'.format(str(initBalance['TWD']['balance']),str(initBalance['USDT']['balance']))
        
        OptionMenu(self.page, self.sellSelf, *self.selloption).grid(row=14, column=1, sticky=EW)
        Button(self.page, text='關閉網格', command=self.close_grid).grid(row=14, column=1, stick=E)
        self.checkOrder()

    def close_grid(self):
        res = askyesno(title = '詢問',message='確定要關閉此網格？')
        if res :
            try:
                if self.sellSelf.get() == self.selloption[0]:
                    self.gd.cancel_all_orders(False)
                    self.msg = '已關閉網格，請手動賣出USDT'
                elif self.sellSelf.get() == self.selloption[1]:
                    self.gd.cancel_all_orders(True)
                    self.msg = '已關閉網格，已自動賣出USDT'
                self.printInfo()
                self.gd.delete_grid()
                self.page.quit()
            except Exception as e:
                self.msg+= 'Error:'+str(e)+'\n(API請求失敗，請確認下單參數及餘額)'

    def now_profit(self):
        nowPrice = self.gd.get_market_price()
        self.gd.new_info['price']=float(nowPrice['buy'])
        NowBalance = float(self.gd.new_info['balance'])+(float(self.gd.new_info['amount'])*float(self.gd.new_info['price']))
            
        self.msg += '網格上限：{} 網格下限：{} 網格數量：{}\n初始總額：{} TWD,  初始價格：{}\n當前總額：{} TWD,  當前買方價格：{}\n已實現利潤：{} {}\n預估年化報酬率：{}% \n\n'.format(
            self.gd.init_info['upper'],
            self.gd.init_info['lower'],
            self.gd.init_info['grid_num'],
            self.gd.init_info['balance'],
            self.gd.init_info['price'],
            NowBalance,
            self.gd.new_info['price'],
            self.gd.realized_profit,
            self.gd.earn_type,
            self.gd.floating_profit)
        self.printInfo()
    
    def grid_list_info(self):
        self.msg+='[價格   ,方向  ,數量   ]\n'
        issell = True
        for i,item in self.gd.all_price_list.items():
            if item['side'] == 'sell' and issell:
                self.msg+='\n'
                issell=False
            if item['side'] !='N':
                self.msg+= str([item['price'],item['side'],item['amount']])+'\n'
        self.printInfo()
         
    def checkOrder(self):
        initBalance = self.gd.get_base_info()
        self.balance['text'] = 'TWD: {} \n USDT: {}'.format(str(initBalance['TWD']['balance']),str(initBalance['USDT']['balance']))
        self.msg = '\n網格進行中..\n\n'
        self.now_profit()
        self.gd.checking_orders()
        self.page.after(90000,self.checkOrder)

    def printInfo(self):
        self.st['state'] = 'normal'	
        self.st.delete('0.0','end')
        self.st.insert('end',str(self.msg)+'\n')
        self.st.update()
        self.msg = ''
        self.st['state'] = 'disabled'	

