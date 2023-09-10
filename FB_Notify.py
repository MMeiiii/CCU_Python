# 載入需要的套件
import datetime
import time
import re
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from subprocess import CREATE_NO_WINDOW
from bs4 import BeautifulSoup
from win10toast_click import ToastNotifier 
import webbrowser

# 開啟瀏覽器視窗(Chrome)
# 方法一：執行前需開啟chromedriver.exe且與執行檔在同一個工作目錄
# driver = webdriver.Chrome()
# 方法二：或是直接指定exe檔案路徑
# driver = webdriver.Chrome(“桌面\chromedriver”)

# ------ 通知 ------
toast = ToastNotifier()

# ------ 設定要前往的網址 ------
url = 'https://www.facebook.com'
#url = 'https://www.facebook.com/groups/696419170371204'

# 設定 "--headless" 不顯示視窗。
#chrome_options = Options()
#chrome_options.add_argument("--headless")

options = webdriver.ChromeOptions()
prefs = {
    'profile.default_content_setting_values':
        {
            'notifications': 2
        }
}
options.add_experimental_option('prefs', prefs)
options.add_argument("headless")
options.add_argument('--disable-gpu')
service = Service()
service.creationflags = CREATE_NO_WINDOW

# ------ 透過Browser Driver 開啟 Chrome ------
#driver = webdriver.Chrome(options=chrome_options)
driver = webdriver.Chrome(options=options, service=service)

# ------ 前往該網址 ------
driver.get(url)

#-------- 讀取關鍵字的file 並建好keyword_list -------
keyword_file= open('keyword.txt', 'r',encoding='utf-8')

keyword_list=[]
for line in keyword_file.readlines():
    keyword_list.extend(line.split(" "))
    
for i in range(0,len(keyword_list)):
    
    keyword_list[i] = keyword_list[i].rstrip()  

# for i in range(0,len(keyword_list)):
#     # print(keyword_list[i])
    
#-------- 把username password 用使用者的帶入------
username = keyword_list[0]
password = keyword_list[1]

# ------ 輸入賬號密碼 ------
WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="email"]')))
elem = driver.find_element(By.ID, "email")
elem.send_keys(username)

elem = driver.find_element(By.ID, "pass")
elem.send_keys(password)        

elem.send_keys(Keys.RETURN)
time.sleep(5)

postID_set = set()

post_div_class = ["kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x c1et5uql ii04i59q", 
                "cxmmr5t8 oygrvhab hcukyx3x c1et5uql o9v6fnle ii04i59q"]
name_div_class = ["oajrlxb2 gs1a9yip g5ia77u1 mtkw9kbi tlpljxtp qensuy8j ppp5ayq2 goun2846 ccm00jje s44p3ltw mk2mc5f4 rt8b4zig n8ej3o3l agehan2d sk4xxmp2 rq0escxv nhd2j8a9 mg4g778l pfnyh3mw p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x tgvbjcpo hpfvmrgz jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso l9j0dhe7 i1ao9s8h esuyzwwr f1sip0of du4w35lb n00je7tq arfg74bv qs9ysxi8 k77z8yql btwxx1t3 abiwlrkh p8dawk7l lzcic4wl oo9gr5id q9uorilb"]
emoji_span_class = ["pq6dq46d tbxw36s4 knj5qynh kvgmc6g5 ditlmg2l oygrvhab nvdbi5me sf5mxxl7 rgmg9uty b73ngqbp", 
                    "pq6dq46d tbxw36s4 knj5qynh kvgmc6g5 ditlmg2l oygrvhab nvdbi5me sf5mxxl7 gl3lb2sf hhz5lgdu"]

#---- 處理html tag for 貼文內容 ----
def getPostText(s):
    # 換行

    for class_name in post_div_class:
        pattern = '<div class="' + class_name + '">(.+)</div>' 
        content = re.findall(pattern, s)
        if(content != []):
            content = content[0]
            s = s.replace('<div class="' + class_name + '">' + content + '</div>', content + '\n')

    pattern = '<div dir="auto" style="text-align:start">(.+?)</div>'
    text_list = re.findall(pattern, s)
    for text in text_list:
        s = s.replace('<div dir="auto" style="text-align:start">' + text + '</div>', text + '\n')
    pattern = '(.+?)<br>'
    text_list = re.findall(pattern, s)
    for text in text_list:
        s = s.replace(text + '<br>', text + '\n')

    # 表情符號
    for class_name in emoji_span_class:
        pattern = '<span class="' + class_name + '"><img alt="(.+?)" height="16" referrerpolicy="origin-when-cross-origin" src="(.+?)" width="16"/></span>'
        emoji_src_list = re.findall(pattern, s)
        for ele in emoji_src_list:
            emoji = ele[0]
            src = ele[1]
            s = s.replace('<span class="' + class_name + '"><img alt="' + emoji + '" height="16" referrerpolicy="origin-when-cross-origin" src="' + src + '" width="16"/></span>', emoji)


    return s

#---- 找尋貼文者名字 ----
def getPosterName(s):
    for class_name in name_div_class:
        pattern = 'aria-label="([^"]+)" class="' + class_name + '"'
        name = re.findall(pattern, s)
        if(name != []):
            return name[0]
    return None
    

#---- 在文章中找尋是否有關鍵字以及是哪些關鍵字 ----
def keyword_find(All_Post_context,keyword_list):
    
    key=0
    keyword_output=[]
    for i in range(2,len(keyword_list)):
        
        if All_Post_context.find(keyword_list[i]) != -1:
            key=1
            # print(keyword_list[i])
            keyword_output.append(keyword_list[i])
        
    if key==1:
            return keyword_output
    else:
            return None

link = ''
def toPostURL():
    webbrowser.open_new(link)
    
path = 'post.txt'
f = open(path, 'w', encoding='utf-8')
print('',end='', file = f) 

while True:
    group_url = 'https://www.facebook.com/groups/875700903111302'
    driver.get(group_url)

    actions = ActionChains(driver)
    for i in range(3):
        actions.send_keys(Keys.END)
        actions.perform()
        time.sleep(2)

    time.sleep(5)
    Group_HTML = driver.page_source
    pattern = '"subscription_target_id":"([0-9]+)"'
    postID_list = re.findall(pattern, Group_HTML)
    pattern = "https://www.facebook.com/groups/875700903111302/posts/([0-9]+)"
    postID_list += re.findall(pattern, Group_HTML)
    #print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    #print(postID)

    for ID in postID_list:
        if ID in postID_set:
            continue
        
        driver.get("https://www.facebook.com/groups/875700903111302/posts/" + ID)
        Post_HTML = driver.page_source
        
        fpath = 'html.txt'
        F = open(fpath, 'w', encoding='utf-8')
        print(Post_HTML, file = F)
        F.close()

        soup = BeautifulSoup(Post_HTML, 'html.parser')

        #---- 尋找貼文內容 ----
        All_Post_context = ''
        for class_name in post_div_class:
            Post_context_list = soup.find_all(attrs={"class": class_name})
            for Post_context in Post_context_list:
                All_Post_context += getPostText(str(Post_context))

        #---- 尋找關鍵字 ----
        Post_keyword_list = keyword_find(All_Post_context,keyword_list)
        if (Post_keyword_list != None):
            link = "https://www.facebook.com/groups/875700903111302/posts/" + ID
            
            Poster_name = getPosterName(Post_HTML)

            if( Poster_name != None):
                title = '貼文中含關鍵字'
                for Post_keyword in Post_keyword_list:
                    title += ' [' + Post_keyword + ']' 

                content = Poster_name + '\n' + All_Post_context
                   
                f = open(path, 'a', encoding='utf-8') 
                print(title, file = f)  
                print(link, file = f)
                print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), file = f)
                print(content + '\n', file = f)
                f.close()

                toast.show_toast(title, content, duration=10, callback_on_click = toPostURL)
        postID_set.add(ID)
        time.sleep(5)


driver.quit()

