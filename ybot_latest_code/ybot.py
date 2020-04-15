from __future__ import unicode_literals

import os
import sys
import redis

from argparse import ArgumentParser

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, VideoMessage, FileMessage, StickerMessage, StickerSendMessage
)
from linebot.utils import PY3

#content need

import requests
from bs4 import BeautifulSoup

import datetime

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)

# obtain the port that heroku assigned to this app.
heroku_port = os.getenv('PORT', None)

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

HOST = "redis-11816.c56.east-us.azure.cloud.redislabs.com"
PWD = "N5PhsiiLAqgj91C7VvcAsQ1kbQacaqjm"
PORT = "11816"

redis1 = redis.Redis(host=HOST, password=PWD, port=PORT)


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if isinstance(event.message, TextMessage):
            handle_TextMessage(event)
        if isinstance(event.message, ImageMessage):
            handle_ImageMessage(event)
        if isinstance(event.message, VideoMessage):
            handle_VideoMessage(event)
        if isinstance(event.message, FileMessage):
            handle_FileMessage(event)
        if isinstance(event.message, StickerMessage):
            handle_StickerMessage(event)
        if isinstance(event.message, LocationMessage):
            handle_LocationMessage(event)

        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

    return 'OK'


# Handler function for Text Message
def handle_TextMessage(event):
    keyword = event.message.text
    user = str(event.source)
    userid = user.split('"')[-2]
    ans = funct_choice(userid,keyword)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(ans)
    )

# Handler function for Sticker Message
def handle_StickerMessage(event):
    line_bot_api.reply_message(
        event.reply_token,
        StickerSendMessage(
            package_id=event.message.package_id,
            sticker_id=event.message.sticker_id)
    )

# Handler function for Image Message
def handle_ImageMessage(event):
    res = str(event)
    line_bot_api.reply_message(
    event.reply_token,
    TextSendMessage(text=res)
    )

# Handler function for Video Message
def handle_VideoMessage(event):
    url = str(event)
    line_bot_api.reply_message(
    event.reply_token,
    TextSendMessage(text=url)
    )

def handle_LocationMessage(event):
    information = str(event)
    line_bot_api.reply_message(
    event.reply_token,
    TextSendMessage(text=information)
    )


# Handler function for File Message
def handle_FileMessage(event):
    information = str(event)
    line_bot_api.reply_message(
    event.reply_token,
    TextSendMessage(text=information)
    )

#demend judge
def typejudge(string):
    type = string.split()[0]
    if type == 'shopping':
        res = search_taobao(''.join(string.split()[1:]))
    elif type == 'rumor':
        res = rumor_dict(''.join(string.split()[1:]))
    elif type == 'disease':
        # res = disease_progress(string.split()[1],string.split()[2])
        res = daily_dict(''.join(string.split()[1:]))
    elif type == 'map':
        res = "https://goo.gl/maps/ya2eKbUPcaqZzcm77"
    else:
        res = search_news(string)
    return res

# taobao item search
# better strain in next version
def search_taobao(keyword):

    web_taobao = "https://list.tmall.com/search_product.htm"

    headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
            }

    params = {
            "q": keyword,
            "type": "p",
            "spm": "a220m.1000858.a2227oh.d100",
            "from": ".list.pc_1_searchbutton"
            }

    res = requests.get(web_taobao, headers=headers, params=params)
    soup = BeautifulSoup(res.text, 'html.parser')
    items = soup.find_all("div", class_="product")

    answer = ''
    for i in range(3):
        item = items[i]
        productPrice = item.find("p", class_="productPrice").text.strip()
        try:
            productTitle = item.find("p", class_="productTitle").text.strip()
        except:
            productTitle = item.find("div", class_="productTitle productTitle-spu").text.strip()
        productShop = item.find("div", class_="productShop").text.strip()
        try:
            productStatus = item.find("p", class_="productStatus").text.strip()
        except:
            productStatus = "暂无"

        answer = "Here is the most popular recommend: "+str(productTitle)+'. Price: '+str(productPrice)+'. You can buy it in '+str(productShop)+". Do you want see others?"

    return answer

def search_news(keyword):
    baidu_news = "https://www.baidu.com/s?rtt=1&bsst=1&cl=2&tn=news&rsv_dl=ns_pc&word="+keyword

    headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
            }

    res = requests.get(baidu_news, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    items = soup.find_all("div", class_="result")
    res = "Here are 3 relative news:"

    for i in range(3):
        item = items[i]
        newsTitle = item.find("h3", class_="c-title").text.strip()
        link = item.find("h3", class_="c-title").find("a")['href']
        res = res+newsTitle+':'+link+'\n'
    return res

# rumor judge by stored in json
# type code = 1
def rumor_judge(keywords):
    keywords_set = set(keywords.split())
    with open('rumour.json', 'r', encoding='utf-8') as f:
        x = json.load(f)
        output_text = 'Oh i think the news '

    for item in x:
        if x[item] is not None:
            for tmp in x[item]:
                tmp_set = set(tmp['title'].split())
                if keywords_set.issubset(tmp_set):
                    output_text = output_text+tmp["title"]+" is "+tmp['TF']
                    return output_text
    return "Sorry i dont know. You can try ask me after days"

#to be changed to store in redis in next version
def rumor_dict(keywords):
    keywords_set = set(keywords.split())
    rumor = {}
    rumor["Corona Virus Disease 2019 In HKBU"] = False
    rumor["Corona Virus Disease 2019 In USA"] = False
    rumor["Corona Virus Disease 2019 In CHINA"] = True
    output_text = 'Oh i think the news '

    for tmp in rumor.keys():
        tmp_set = set(tmp.split())
        if keywords_set.issubset(tmp_set):
            output_text = output_text + tmp + " is " + str(rumor[tmp])
            return output_text
    return "Sorry i dont know. You can try ask me after days"

def demend(sentense):
    words = sentense.lower().split()
    stop_words = ['a','the','i','an','he','she','very','so','to','for','that','this']
    selected = []
    for word in words:
        if word not in stop_words:
            selected.append(word)
    return selected

def funct_intend(sentense):
    words = lang_pres_layer(sentense)
    # verus_keyword = ['situation','number','confirmed','suspected']
    # rumor_keyword = ['true','false','if']
    # purchase_keyword = ['buy','price','mask','medicine']
    # news_keyword = ['news','hear','heard','thing']
    fun_dict = {'situation':0,'number':0,'confirmed':0,'suspected':0,'true':1,'false':1,'if':1,'buy':2,'price':2,'mask':2,'medicine':2,'news':3,'hear':3,'heard':3,'thing':3}
    count = [0,0,0,0]
    for word in words:
        if word in fun_dict.keys():
            count[fun_dict[word]] = count[fun_dict[word]]+1
    max = 0
    max_id = -1
    for id,num in enumerate(count):
        if num > max:
            max = num
            max_id = id
    res_dict = {-1:'default',0:'verus',1:'rumor',2:'purchase',3:'news'}
    return res_dict[max_id]

def session_store(id,status_code,period_code):
    now_time = datetime.datetime.now().strftime('%F-%H-%M')
    time_visit = now_time
    sess_code = str(status_code)+'_'+str(period_code)+'_'+str(time_visit)
    redis1.set(f'{id}#session', sess_code)
    redis1.expire(f'{id}#session',900)
    print(redis1.ttl(f'{id}#session'))
    return sess_code

def session_get(id):
    session = redis1.get(f'{id}#session')
    if session is not None:
        return session.decode()
    else:
        return ''

def virus_check():
    date = datetime.datetime.now().strftime('%F')

    session = redis1.get(f'{date}#virus')
    if session is not None:
        data = int.from_bytes(session, 'big')
        return data
    else:
        return ''

def map_search(keyword):
    loc_website = redis1.get(keyword)
    if loc_website is not None:
        return loc_website
    else:
        return "sorry not recorded in now. maybe you can try other places?"

def virus_store(num):
    date = datetime.datetime.now().strftime('%F')
    redis1.set(f'{date}#virus', num.to_bytes(4, 'big'))
    redis1.expire(f'{date}#virus',86400)

def shopping_get(item_name):
    item_content = redis1.get(f'{item_name}#itemcontent')
    if item_content is not None:
        return item_content.decode()
    item_num = redis1.get(f'{item_name}#itemname')
    if item_num is None:
        item_num = 1
        redis1.set(f'{item_name}#itemname',item_num.to_bytes(4,'big'))
    else:
        item_num = int.from_bytes(item_num,'big')+1
    return item_num

def shopping_record(item_name,content):
    if redis1.exists(f'{item_name}#itemname'):
        redis1.delete(f'{item_name}#itemname')
    redis1.set(f'{item_name}#itemcontent',content)
    return 1

def latest_corn_news(keyword):
    html = 'https://www.medicinenet.com/coronavirus/focus.htm'

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
    }

    res = requests.get(html, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    items = soup.find_all("div", class_="result")
    res = "Here are 3 relative news:"

    for i in range(3):
        item = items[i]
        newsTitle = item.find("ul", class_="c-title").text.strip()
        link = item.find("h3", class_="c-title").find("a")['href']
        res = res + newsTitle + ':' + link + '\n'
    return res



def symptom_checker():
    checker = "https://www.medicinenet.com/symptoms_and_signs/symptomchecker.htm#introView"
    res = "maybe you can go this website to check"+checker
    return res

def status_suspecting(status_code):
    HOST = "redis-11816.c56.east-us.azure.cloud.redislabs.com"
    PWD = "N5PhsiiLAqgj91C7VvcAsQ1kbQacaqjm"
    PORT = "11816"

    redis1 = redis.Redis(host=HOST, password=PWD, port=PORT)

    msg = 'test_code'

    data = redis1.get(f'{msg}#wym')
    if data is not None:
        data = int.from_bytes(data, 'big')
    redis1.set(f'{msg}#wym', status_code.to_bytes(4, 'big'))
    return data


def get_hk_num(start_time,end_time):
    file_version = "https://api.data.gov.hk/v1/historical-archive/list-file-versions"

    url = "http://www.chp.gov.hk/files/misc/latest_situation_of_reported_cases_covid_19_eng.csv"
    start = start_time #YYYYMMDD
    end = end_time

    data = {'url': url, 'start': start, 'end': end}

    req = requests.get(file_version, data)
    if req.json()['timestamps']!=[]:
        version = req.json()['timestamps'][0]

        api_terminal = "https://api.data.gov.hk/v1/historical-archive/get-file"

        data = {'url':url,'time':version}

        req = requests.get(api_terminal,data)
        dic = req.text
        return dic
    else:
        return -1

def api_search():
    # date format :YYYYMMDD
    now_time = datetime.datetime.now()
    de_date = ((now_time + datetime.timedelta(days=-1)).strftime("%Y%m%d"))
    api_res = get_hk_num(de_date, de_date)
    try:
        res = int(api_res.split()[-1].split(',')[2])
    except:
        res = -1
    # if api_res != -1:
    #     res = "Till "+de_date+" there are "+str(api_res.split()[-1].split(',')[2])+" confirmed cases in HongKong"
    # else:
    #     res = "Yesterday's latest record is still not recorded yet"
    return res

def search_disease(keyword):
    keyword = keyword.split()
    html = "https://search.nih.gov/search?utf8=%E2%9C%93&affiliate=nih&query=headache&commit=Search"

    headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
            }

    res = requests.get(html, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    items = soup.find("div", class_ = "content-block-item med-topic")
    href = items.find("h4").find("a")['href']

    new_res = requests.get(href, headers = headers)
    new_soup = BeautifulSoup(new_res.text,'html.parser')
    # print(new_soup)
    div_hold = new_soup.find("div", id = "topic-summary")
    p = div_hold.find_all("p")
    answer = ""
    for tmp in p:
        if tmp.string is not None:
            answer = answer+tmp.string
    answer = answer + '. \nif you want know more, can reference this website: '+href
    return answer

def funct_choice(userid,sentense):
    sess_length = len(session_get(userid))
    session = session_get(userid).split('_')
    answer = ''
    if sess_length == 0:
        #session_store(id,0,0)
        answer = "Hi, this is ybot. Tell me what you want with the number:\n 1.coniv news 2.health care 3.coniv latest condition 4.buy epidemic prevention products 5.over this function 6.nearby hospital"
        session_store(userid,-1,-1)
    elif sentense == '5':
        session_store(userid,-1,-1)
        answer = "oh please retell me the number of function you want"
    elif sentense == '3':
        tmp = virus_check()
        if tmp == -1:
            ans = api_search()
            virus_store(ans)
            tmp = str(ans)
        else:
            tmp = str(tmp)
        answer = "Now in Hong Kong reported num has acchieved " + tmp + ". You'd better stay inside more and take good care of yourself. Don't worry, it will turn off soon"
        session_store(userid, 3, 0)
        return  answer
    elif session[0] == '-1':
        if sentense == '1':
            answer = "oh what news do you want to know?"
            session_store(userid,1,0)
        elif sentense == '2':
            answer = "Do you feel bad? if so "+symptom_checker()+" or tell me the symptom you want to know"
            session_store(userid,2,0)
        elif sentense == '4':
            answer = "what do you want to buy? I can give you some recommmend in Taobao"
            session_store(userid,4,0)
        elif sentense == '6':
            answer = "where do you live, i mean, such as Monkok?"
            session_store(userid,6,0)
    elif session[0] == '1':
        answer = search_news(sentense)
    elif session[0] == '2':
        answer = search_disease(sentense)
    elif session[0] == '4':
        answer = search_taobao(sentense)
    elif session[0] == '6':
        answer = map_search(keyword)
    else:
        answer = "Now i'm waiting for you to enter keyword for function" + str(session[0]) +". If you want to over, just enter 5"
    session = session_get(userid).split('_')
    print(session)
    return answer


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(host='0.0.0.0', debug=options.debug, port=heroku_port)


