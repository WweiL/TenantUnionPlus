from bs4 import BeautifulSoup
def test():
    soup = BeautifulSoup(open("pag1.html"), 'html.parser')
    address = []
    for link in soup.find_all('a'):
        url = link.get('href')
        url = "https://tenantunion.illinois.edu" + str(url)
        br1 = link.findNext('br')
        property_type = br1.nextSibling
        br2 = property_type.findNext('br')
        beds = br2.nextSibling
        br3 = beds.findNext('br')
        baths = br3.nextSibling
        br4 = baths.findNext('br')
        Address = br4.nextSibling
        br5 = Address.findNext('br')
        rent = br5.nextSibling
        Address = str(Address)
        Address = Address.replace('\n', '')
        Address = Address.replace('\t', '')
        Address = Address.replace(' ', '')
        Address = Address.replace('Address:', '')
        Address = Address.replace('61801', '')
        Address = Address.replace('61820', '')
        address.append(Address)
        print(beds)
        # print(url, str(property_type).lstrip(), str(beds).lstrip(), str(baths).lstrip(), str(Address).lstrip(), str(rent).lstrip())
    return beds
