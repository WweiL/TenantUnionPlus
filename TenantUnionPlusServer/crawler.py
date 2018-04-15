import re
import os
import sys
import random

import requests
from bs4 import BeautifulSoup
#from http.cookiejar import LWPCookieJar
# for py2
# from http.cookiejar import LWPCookieJar
from cookielib import LWPCookieJar

requests = requests.Session()
requests.cookies = LWPCookieJar('cookies')
try:
    requests.cookies.load(ignore_discard=True)
except:
    pass


def get_house_info():
    username = "ruimeng2"
    password = "Wszgr123!"

    url = "https://login.uillinois.edu/auth/IllinoisLogin/sm_login.fcc?TYPE=33554433&REALMOID=06-b81d655f-a916-4815-a94b-1e087c2f0111&GUID=&SMAUTHREASON=0&METHOD=GET&SMAGENTNAME=-SM-Y2WdlU%2fpnFMTmAPypPFoZXRghDPs6uCzCBvqiybMgjUmNXVjtrWQCS9HPg2iSnyZ&TARGET=-SM-HTTPS%3a%2f%2ftenantunion%2eillinois%2eedu%2fsm%2flogin%2easp%3fURL%3d%2fhousingexplorer%2fStudent%2fSearchApartment%2easpx"

    headers = {
        'Accept': 'image/webp,image/*,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh',
        'Connection': 'keep-alive',
        'Origin':'https://tenantunion.illinois.edu',
        'Cache-Control':'private',
        'Refer':'https://tenantunion.illinois.edu/housingexplorer/login.aspx',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    }

    form = {
        'USER': username,
        'PASSWORD': password,
        "SMENC": "ISO-8859-1",
        "SMLOCALE": "US-EN",
        "queryString": "null",
        #"target: "HTTPS://tenantunion.illinois.edu/sm/login.asp?URL=/housingexplorer/Student/SearchApartment.aspx",
        "smquerydata": "",
        "smauthreason": "0",
        "smagentname": "Y2WdlU/pnFMTmAPypPFoZXRghDPs6uCzCBvqiybMgjUmNXVjtrWQCS9HPg2iSnyZ",
        "postpreservationdata":""
    }

    r = requests.post(url, headers=headers, data=form)

    pageSource = r.content
    soup = BeautifulSoup(pageSource, "html.parser")
    address = []
    bed = []
    bath = []
    rent = []
    electricity = []
    water = []
    internet = []
    furnished = []
    tv = []
    dishwasher = []
    urls = []
    images = []

    for a in soup.find_all('a', href=True):
        if a['href'].startswith("/housingexplorer/Student/"):
            url = str("https://tenantunion.illinois.edu" + a['href'].encode('utf-8'))
            urls.append(url)
            r = requests.get(url)
            pageSource = r.content
            soup = BeautifulSoup(pageSource, "html.parser")
            # print ("Found the URL:", url)
            # page_content = soup.find('div', {'id': 'ContentPlaceHolder1_pnlSearch'})
            images.append(get_image(soup.find('div', {"id": "galleria"})))
            for p in soup.find_all('p'):
                prop = preprocess(p.getText())
                if prop == 'Address:':
                    addr = get_address(((p.findNext('td').findNext('span'))))
                    if "/" in addr:
                        continue
                    if addr != "ContactInfo":
                        address.append(addr)
                if prop == 'Beds:':
                    bed.append(general(p.findNext('td')))
                if prop == 'Baths:':
                    bath.append(general(p.findNext('td')))
                if prop == 'Rent:':
                    rent.append(general(p.findNext('td')))
                if prop == 'Electricity:':
                    electricity.append(1 if general(p.findNext('td')) == 'Yes' else 0)
                if prop == 'Water:':
                    water.append(1 if general(p.findNext('td')) == 'Yes' else 0)
                if prop == 'Internet:':
                    internet.append(1 if general(p.findNext('td')) == 'Yes' else 0)
                if prop == 'TV:':
                    tv.append(1 if general(p.findNext('td')) == 'Yes' else 0)
                if prop == 'Furnished:':
                    furnished.append(1 if general(p.findNext('td')) == 'Yes' else 0)
                if prop == 'Dishwasher:':
                    dishwasher.append(1 if general(p.findNext('td')) == 'Yes' else 0)

    return images, urls, address, bed, bath, rent, electricity, water, internet, furnished, tv, dishwasher

def preprocess(string):
    string = string.encode('utf-8')
    string = string.replace('\n', '')
    string = string.replace('\t', '')
    string = string.replace('\r', '')
    string = string.replace(' ', '')
    return string
    
def get_address(td):
    addr = str(preprocess(td.getText().split("618")[0]))
    # print("asds", addr)
    return addr

def general(td):
    item = preprocess(td.getText())
    return item

def get_image(div):
    i = 0
    img_list = []
    prefix = 'https://tenantunion.illinois.edu/housingexplorer'
    for img in div.find_all('img'):
        img_list.append((prefix + img['src'].replace('..', '')).encode('utf8'))
        i += 1
        if i == 5:
            break
    while i < 5:
        img_list.append('https://tenantunion.illinois.edu/housingexplorer/ShowImage.ashx?id=1&iteration=1&AID=3191')
        i += 1
    return img_list
    
""""
    r = requests.post("https://tenantunion.illinois.edu/housingexplorer/Student/PropertyDetails.aspx?aid=3149&Lid=4058")
    with open('f.tx','w+') as input:
        input.write(str(r.content))

    r = requests.post("https://tenantunion.illinois.edu/housingexplorer/Student/PropertyDetails.aspx?aid=50&Lid=16")
    with open('f.tx', 'w+') as input:
        input.write(str(r.content))
"""

    # if not r.headers['Content-Type'].endswith('GBK'):
    #     print u'Login success'
    # else:
    #     print u'Login error'
    # requests.cookies.save()
    # print r.status_code
    #
    # year_term_no = 21  # from bottom to end,2012-2013
    #
    # base_url = "http://jw.hrbeu.edu.cn/ACTIONQUERYELECTIVERESULTBYSTUDENT.APPPROCESS"
    #
    # r = requests.get(base_url)
    #
    # with open('temp.html', 'w+') as t:
    #     t.write(r.content)
    # base_soup = BeautifulSoup(r.content, "lxml")
    #
    # student_name = base_soup.find('td').get_text()
    # print student_name

def test():
    soup = BeautifulSoup(open("pag1.html"), 'html.parser')
    address = []
    bed = []
    bath = []
    rent = []
    url = []
    for link in soup.find_all('a'):
        URL = link.get('href')
        URL = "https://tenantunion.illinois.edu" + str(URL)
        br1 = link.findNext('br')
        property_type = br1.nextSibling
        br2 = property_type.findNext('br')
        Beds = br2.nextSibling
        br3 = Beds.findNext('br')
        Baths = br3.nextSibling
        br4 = Baths.findNext('br')
        Address = br4.nextSibling
        br5 = Address.findNext('br')
        Rent = br5.nextSibling
        Address = process_address(Address)
        Beds = process_beds(Beds)
        Baths = process_baths(Baths)
        Rent = process_rent(Rent)
        address.append(Address)
        bed.append(Beds)
        bath.append(Baths)
        rent.append(Rent)
        url.append(URL)
        
    return address, bed, bath, rent, url

def process_address(Address):
    Address = preprocess(Address)
    Address = Address.replace('Address:', '')
    Address = Address.replace('61801', '')
    Address = Address.replace('61820', '')
    return Address

def process_beds(beds):
    beds = preprocess(beds)
    beds = beds.replace('Beds:', '')
    return beds
    
def process_baths(baths):
    baths = preprocess(baths)
    baths = baths.replace('Baths:', '')
    return baths

def process_rent(rent):
    rent = preprocess(rent)
    rent = rent.replace('Rent:', '')
    return rent

if __name__ == '__main__':
    get_house_info()
