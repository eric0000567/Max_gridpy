import webbrowser
from CreatePage import *
import requests

dataURL = 'https://script.google.com/macros/s/AKfycbwBCAOlZvtzGFG8ZVeA0qHGxaqO1dXCSo-A0V_t_UVAE1pVbEO_LZEL-Rx4wwTTpYi2/exec'
r = requests.get(dataURL)
data = r.json()[0]['data']

class LoginPage(object):
    def __init__(self, master=None):
        self.root = master #定義內部變數root
        self.root.geometry('%dx%d' % (600, 300)) #設定視窗大小
        self.phone = StringVar()
        self.key = StringVar()
        self.screct = StringVar()
        self.createPage()

    def createPage(self):
        self.page = Frame(self.root) #建立Frame
        self.page.pack()
        Label(self.page).grid(row=0, stick=W)

        Label(self.page, text = '電話號碼: ').grid(row=1, stick=W, pady=10)
        Entry(self.page, textvariable=self.phone).grid(row=1, column=1, stick=E)
        Label(self.page, text = 'MAX API Key: ').grid(row=2, stick=W, pady=10)
        Entry(self.page, textvariable=self.key).grid(row=2, column=1, stick=E)		
        Label(self.page, text = 'MAX Screct Key: ').grid(row=3, stick=W, pady=10)
        Entry(self.page, textvariable=self.screct).grid(row=3, column=1, stick=E)
        Button(self.page, text='退出', command=self.page.quit).grid(row=4, stick=W, pady=10)
        Button(self.page, text='登入', command=self.loginCheck).grid(row=4, column=1, stick=E)		
        gateregister = Label(self.page, text='點我註冊MAX(享手續費「半價」優惠)', fg="blue", cursor="hand2")
        gateregister.grid(row=5, columnspan=2, stick=W)
        gateregister.bind("<Button-1>", lambda e: self.callback("https://max.maicoin.com/signup?r=5a7b91b7"))
        
    

    def callback(self,url):
        webbrowser.open_new(url)

    def loginCheck(self):
        phone = self.phone.get()
        key = self.key.get()
        screct = self.screct.get()
        checkAcc = False
        for d in data:
            if phone==d['phone']:
                checkAcc = True
                break
        if checkAcc:
            try:
                self.page.destroy()
                CreateGrid(self.root,key,screct)
            except Exception as e:   
                showinfo(title='錯誤', message='API KEY錯誤！請再次檢查是否輸入正確或是否開通此API！')
        else:
            showinfo(title='錯誤', message='查無電話號碼！請購買授權！')

