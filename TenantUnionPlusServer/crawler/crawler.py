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
        address.append(Address)
        # print(url, str(property_type).lstrip(), str(beds).lstrip(), str(baths).lstrip(), str(Address).lstrip(), str(rent).lstrip())
    return address
# for br in soup.findAll('br'):
#     next_s = br.nextSibling
#     if not (next_s and isinstance(next_s,NavigableString)):
#         continue
#     next2_s = next_s.nextSibling
#     if next2_s and isinstance(next2_s,Tag) and next2_s.name == 'br':
#         text = str(next_s).strip()
#         if text:
#             print "Found:", next_s
#
# address = soup.find(text="Address:")
# b_tag = address.parent
# td_tag = b_tag.parent
# next_td_tag = td_tag.findNext('td')
# print next_td_tag.contents[0]
