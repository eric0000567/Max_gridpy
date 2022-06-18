from tkinter import *
from venv import create
from grid import *
from tkinter.scrolledtext import ScrolledText
from tkinter.messagebox import *
import multiprocessing as mp

class MainPage(object): # 狀態總覽
    def __init__(self, master=None,key='',screct=''):
        self.root = master
        self.root.geometry('%dx%d' % (800, 600))
        self.gd = Grid(key,screct)
        self.upper = StringVar()
        self.lower = StringVar()
        self.gradeNum = StringVar()
        self.earn_type = StringVar()
        self.optionList = ["TWD", "USDT"]
        self.earn_type.set(self.optionList[0])
        self.grid_balance = StringVar()

        self.sellSelf = StringVar()
        self.selloption = ["不做任何動作", "賣出所有網格持倉"]
        self.sellSelf.set(self.selloption[0])
        self.createPage()

    def createPage(self):
        self.page = Frame(self.root) #建立Frame
        self.page.pack()
        Label(self.page).grid(row=0, stick=W)
        showinfo(title='警告', message='若關閉此程式網格將停止運行！！\n此網格每90秒檢查一次')

        Label(self.page, text = '當前資產狀態').grid(row=0, column=0,columnspan=2, stick=EW, pady=10)
        self.balance = Label(self.page, text = '...')
        self.balance.grid(row=1,columnspan=2, stick=EW, pady=5)
        
        self.nowPrice = Label(self.page, text = '當前USDT價格：')
        self.nowPrice.grid(row=2, column=0, stick=W, pady=5)

        Label(self.page, text = '賺什麼?').grid(row=3, column=0, stick=W, pady=5)
        OptionMenu(self.page, self.earn_type, *self.optionList).grid(row=3, column=1, sticky=W)

        Label(self.page, text = '網格上限：').grid(row=4, column=0, stick=W, pady=5)
        Entry(self.page, textvariable=self.upper).grid(row=4, column=1, stick=W, pady=5)
        Label(self.page, text = '網格下限：').grid(row=5, column=0, stick=W, pady=5)
        Entry(self.page, textvariable=self.lower).grid(row=5, column=1, stick=W, pady=5)
        Label(self.page, text = '網格數量：').grid(row=6, column=0, stick=W, pady=5)
        Entry(self.page, textvariable=self.gradeNum).grid(row=6, column=1, stick=W, pady=5)
        Button(self.page, text='計算報酬', command=self.count_grade_profit).grid(row=7, column=1, stick=E)
        Label(self.page, text = '開單金額：').grid(row=10, column=0, stick=W, pady=5)
        Entry(self.page, textvariable=self.grid_balance).grid(row=10, column=1, stick=W, pady=5)

        Button(self.page, text='創建網格', command=self.create_grid).grid(row=11, column=1, stick=E)
        Button(self.page, text='查看網格資訊', command=self.now_profit).grid(row=12, column=0, stick=E)
        Button(self.page, text='查看當前掛單', command=self.grid_list_info).grid(row=12, column=1, stick=W)

        self.msg = ''
        self.st = ScrolledText(self.page,height=10)
        self.st.grid(row=13, columnspan=2, stick=W, pady=5)

        self.nowPrice['text'] = '當前USDT價格：{}'.format(str(self.gd.get_market_price()['sell']))
        initBalance = self.gd.get_base_info()
        self.balance['text'] = 'TWD: {} \n USDT: {}'.format(str(initBalance['TWD']['balance']),str(initBalance['USDT']['balance']))
        
        self.gd.earn_type = self.earn_type.get()
        
        OptionMenu(self.page, self.sellSelf, *self.selloption).grid(row=14, column=1, sticky=EW)
        Button(self.page, text='關閉網格', command=self.close_grid).grid(row=14, column=1, stick=E)

    def close_grid(self):
        try:
            if self.sellSelf.get() == self.selloption[0]:
                self.gd.cancel_all_orders(False)
                self.msg = '已關閉網格，請手動賣出USDT'
            elif self.sellSelf.get() == self.selloption[1]:
                self.gd.cancel_all_orders(True)
                self.msg = '已關閉網格，已自動賣出USDT'
            self.printInfo()
        except Exception as e:
            self.msg+= 'Error:'+str(e)+'\n(API請求失敗，請確認下單參數及餘額)'

    def now_profit(self):
        self.msg += '初始總額：{} TWD,  初始價格：{}\n當前總額：{} TWD,  當前價格：{}\n已實現利潤：{} {}\n預估年化報酬率：{}% \n\n'.format(
            self.gd.init_info['balance'],
            self.gd.init_info['price'],
            self.gd.new_info['balance']+(self.gd.new_info['amount']*self.gd.new_info['price']),
            self.gd.new_info['price'],
            self.gd.realized_profit,
            self.gd.earn_type,
            self.gd.floating_profit)
        self.printInfo()

    def grid_list_info(self):
        self.msg+='[價格   ,方向  ,數量  ]\n'
        issell = True
        for i,item in self.gd.all_price_list.items():
            if item['side'] == 'sell' and issell:
                self.msg+='\n'
                issell=False
            if item['side'] !='N':
                self.msg+= str([item['price'],item['side'],item['amount']])+'\n'
        self.printInfo()
        
        
    def count_grade_profit(self):
        self.nowPrice['text'] = '當前USDT價格：{}'.format(str(self.gd.get_market_price()['sell']))
        data = self.gd.count_grade_profit(
            float(self.upper.get()),
            float(self.lower.get()),
            int(self.gradeNum.get()))
        self.msg +='價差間隔：{}'.format(str(data['grade']))+'\n'
        self.msg +='報酬率(已扣除手續費)：{}% ~ {}%'.format(str(data['profit']['min']),str(data['profit']['max']))+'\n'
        self.msg +='最少使用：{} 台幣'.format(str(data['least']))+'\n\n'
        self.printInfo()

    def create_grid(self):
        self.count_grade_profit()
        self.msg += '創建中..請稍後..'
        self.printInfo()
        creating = self.gd.create_all_price_list(
            float(self.upper.get()),
            float(self.lower.get()),
            int(self.gradeNum.get()),
            float(self.grid_balance.get()))
        if not creating:
            self.msg += '餘額不足！'
            self.printInfo()
            return
        placeMsg = self.gd.place_order()
        if placeMsg =='done':
            self.msg+= '網格創建完成!\n'
            self.printInfo()
            self.checkOrder()
        else:
            self.msg+= 'Error:'+placeMsg+'\n(API請求失敗，請確認下單參數及餘額)'
        self.printInfo()


    def checkOrder(self):
        self.nowPrice['text'] = '當前USDT價格：{}'.format(str(self.gd.get_market_price()['sell']))
        initBalance = self.gd.get_base_info()
        self.balance['text'] = 'TWD: {} \n USDT: {}'.format(str(initBalance['TWD']['balance']),str(initBalance['USDT']['balance']))
        self.gd._record()
        self.msg = '\n網格進行中..\n\n'
        self.now_profit()
        self.page.after(90000,self.checkOrder)

    def printInfo(self):
        self.st['state'] = 'normal'	
        self.st.delete('0.0','end')
        self.st.insert('end',str(self.msg)+'\n')
        self.st.update()
        # self.page.after(1000,self.printInfo)
        self.msg = ''
        self.st['state'] = 'disabled'	

