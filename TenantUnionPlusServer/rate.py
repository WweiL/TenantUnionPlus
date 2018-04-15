def get_home_dict():
    db = get_db()
    c = db.cursor()
    c.execute("SELECT location,rscore,gymscore,marketscore,libraryscore,north,out  FROM room")
    h=c.fetchall()
    c.execute("SELECT COUNT(*) FROM room")
    count=c.fetchone()
    count=count[0]
    home_dict=[]
    for i in range(count):
        home_dict.append([h[i][0],h[i][1],h[i][2],h[i][3],h[i][4],h[i][5],h[i][6]])
    home_dict=np.array(home_dict)
    return home_dict

def score(location,gym,eat,car,study):
    #rscore=list[0]
    #rscore=srestaurantrate*srscore+orestaurantrate*orscore
    home_dict=get_home_dict()
    restaurantrate=0.3
    gymrate=0.1
    marketrate=0.3
    libraryrate=0.2
    nsrate=1.0
    """if ('year' == 'fresh'):
        srestaurantrate = 0.8
        orestaurantrate = 0.2
    else:
        srestaurantrate = 0.1
        orestaurantrate = 0.9"""

    ###For location,question2:
    # north==1,south==0



    ###For gym, question3:
    if (gym == 1.0):
        gymrate = 0.1
    elif (gym == 2.0):
        gymrate = 0.15
    elif (gym == 3.0):
        gymrate = 0.25
    else:
        gymrate = 0.3

    ###For question4:
    # cook==1
    if (eat == 1.0):
        restaurantrate = 0.25
        marketrate = 0.7

    ###For question5##  :
    # car==1

    if (car == 0.0):
        newhome_dict=[]
        for i in range(home_dict.shape[0]):
            if (home_dict[i][6].astype(float) == 0):  ##This means that the house is not on campus:
                newhome_dict.append(home_dict[i])
        home_dict = np.array(newhome_dict)

    ###For question6
    #library=0
    if (study == 0.0):
        libraryrate = 0.3
    #print(home_dict)
    #rscore=srestaurantrate*srscore+orestaurantrate*orscore
    result=[]
    for i in range(home_dict.shape[0]):
        # north==1,south==0
        if (location == 1) and (home_dict[i][5].astype(float) == 0):
            ###This means if the house is in the north, house is equal to zero
            nsrate = 0.66666666
        elif (location == 0) and (home_dict[i][5].astype(float) == 1):
            ###This means if the house is in the south house is equal to one
            nsrate = 0.66666666
        restaurantscore=home_dict[i][1].astype(float)
        gymscore=home_dict[i][2].astype(float)
        marketscore=home_dict[i][3].astype(float)
        libraryscore=home_dict[i][4].astype(float)
        finalscore=(nsrate*(restaurantrate*restaurantscore+gymrate*gymscore+marketrate*marketscore+libraryrate*libraryscore))/(restaurantrate+gymrate+marketrate+libraryrate)
        result.append([home_dict[i][0],finalscore])
    result=np.array(result)
    #print(result)
    result = result[result[:,-1].argsort()]
    #print(result)
    return result

def give_result_lat_lng(location, gym, eat, car, study):
    db = get_db()
    c = db.cursor()
    result=score(location,gym,eat,car,study)
    lat_lng=[]
    for i in range(result.shape[0]):
        c.execute("SELECT lat,lng FROM room WHERE location=?",[result[i][0]])
        answer=c.fetchone()
        lat_lng.append([answer[0],answer[1]])
    lat_lng=np.array(lat_lng)
    return lat_lng

# @app.cli.command('main')
# def main_():
#     result=give_result_lat_lng(0,1,0,0,1)
#     print(result)
