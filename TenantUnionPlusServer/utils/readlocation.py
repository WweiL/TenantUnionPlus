from urllib import request
a=''
b=''
url = r'https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&key=AIzaSyDZNR0tka_TdxqMhxxkCbTbvcMJ-lwzgVY'
res = request.urlopen(url)
html = res.read().decode('utf-8')
with open("latitude_longtitude.txt","w") as f:
    f.write(html)
file=open("latitude_longtitude.txt")
line=file.readlines()
a=line[58]
b=line[59]
file.close()
a=a[23:32]
b=b[23:32]
print(a)
print(b)
