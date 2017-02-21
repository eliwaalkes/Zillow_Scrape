from bs4 import BeautifulSoup
import urllib.request
import re
import pickle


def save_object(obj, filename):
    with open(filename, 'wb') as output:
        pickle.dump(obj, output, -1)

def load_object(filename):
    file = open(filename, 'rb')
    return pickle.load(file)



def house_ids(id):
    #id can be city name or zip code
    urls = []
    for i in range(1,2):
        url = urllib.request.urlopen("https://www.zillow.com/homes/" + id + "_rb/" + str(i) + "_p/").read()
        soup = BeautifulSoup(url)
        search_results = soup.find('ul', attrs={'class' : "photo-cards"})
        for li in search_results:
            urls.append(li.contents[0]['data-zpid'])

    return urls

def check_facts(k):
    if(k[:3] != "<di"): return False
    if (k[:2] != "<a"): return False
    return True

def check_desc(k):
    if(k[:4] != "<div"): return False
    if(k[:3] != "<br"): return False
    return True

def save_house_data(id):
    id = id + "_zpid"
    url = "http://www.zillow.com/homedetails/" + id
    page = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(page)

    STUFF = {}
    try:
        address = soup.find('h1', attrs={'class':"notranslate"}).contents[0][:-2]
        STUFF["address"] = address

        city = soup.find('span', attrs={'class':"zsg-h2 addr_city"}).contents[0]
        STUFF["city"] = city

        bbs = soup.findAll('span', attrs={'class':"addr_bbs"})

        beds = bbs[0].contents[0].replace(",", "")
        STUFF["beds"] = int(re.search(r'\d+', beds).group())

        baths = bbs[1].contents[0].replace(",", "")
        STUFF["baths"] = int(re.search(r'\d+', baths).group())

        sqft = bbs[2].contents[0].replace(",", "")
        STUFF["sqft"] = int(re.search(r'\d+', sqft).group())

        listing = soup.find('div', attrs={'class':" status-icon-row for-sale-row home-summary-row"}).contents[2]
        STUFF["listing"] = listing

        price = soup.find('div', attrs={'class':"main-row  home-summary-row"}).contents[1].contents[0].replace(",", "")
        STUFF["price"] = int(re.search(r'\d+', price).group())

        description = ""
        for i in soup.find('div', attrs={'class': "notranslate zsg-content-item"}).contents:
            j = str(i)
            if check_desc(j): description +=  j
        STUFF["description"] = description

        facts = []
        x = soup.findAll('ul', attrs={'class': "zsg-list_square zsg-lg-1-3 zsg-md-1-2 zsg-sm-1-1"})
        for i in x:
            for j in i.findAll('li'):
                k = str(j.contents[0])
                if check_facts(k): facts.append(k)

        STUFF['facts'] = facts
    except (AttributeError, IndexError):
        pass

    return STUFF


def main():
    id = input("Enter a city or a zip code: ")
    zpids = house_ids(id)
    houses = {}
    for i in zpids:
        houses[i] = save_house_data(i)
    #save_object(houses, id + " Housing Data Dictionary")
    file = open("output", 'w+')
    for i,j in houses.items():
        file.write(i + " " + str(j) + "\n\n\n")
    file.close()

main()