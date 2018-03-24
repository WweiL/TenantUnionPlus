from bs4 import BeautifulSoup
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
        
    return address, rent, bed, bath, rent, url

def preprocess(string):
    string = str(string)
    string = string.replace('\n', '')
    string = string.replace('\t', '')
    string = string.replace(' ', '')
    return string

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
