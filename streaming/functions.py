from streaming import models, enums
import hashlib
import jdatetime as jdt
import datetime as dt
import os
import json
import string
import random


# This method starts signup operation
# it will check if username or phone or numberid exist in database
# password will be MD5 hexadecimal hashed .
# birthday will be converted to gregorian date .
# returns standard json response
def signUP(informations):
    userExist = doesUserExist(informations)
    if userExist:
        return userExist
    password = hashlib.md5(informations['password'].encode()).hexdigest()
    bdate = informations['birthdate'].split("/")
    bdate = jdt.datetime(int(bdate[0]), int(bdate[1]), int(bdate[2]))
    bdate = bdate.togregorian()
    now = dt.datetime.now()
    token = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(32))
    newUser = models.User(userName=informations['username'], encryptedPassword=password,
                          fName=informations['fname'], lName=informations['lname'],
                          phone=informations['phone'], numberId=informations['nid'], birthDate=bdate,
                          educationLevel=informations['edlvl'], registerTime=now, token=token)
    # print(newUser)
    newUser.save()
    informations['id'] = newUser.id
    createLog("User Created Successfully", informations)
    return {"result": True, "code": 200, "token": token}


# this method will check if user's username , phone and number id is unique or not
# returns json error in standard type if user exist . otherwise returns None .
def doesUserExist(informations):
    if searchUserByUsername(informations['username']).exists():
        createLog(enums.getDescription(430), informations)
        return {"result": False, "code": 430, "desc": enums.getErrors(430)}
    if searchUserByPhone(informations['phone']).exists():
        createLog(enums.getDescription(431), informations)
        return {"result": False, "code": 431, "desc": enums.getErrors(431)}
    if searchUserByNumberid(informations['nid']).exists():
        createLog(enums.getDescription(432), informations)
        return {"result": False, "code": 432, "desc": enums.getErrors(432)}


def searchUserByToken(token):
    user = models.User.objects.filter(token=token)
    return user


# this method will search database by user's username .
# returns User
def searchUserByUsername(username):
    user = models.User.objects.filter(userName__iexact=username)
    return user


# this method will search database by user's phone .
# returns User
def searchUserByPhone(phone):
    user = models.User.objects.filter(phone=phone)
    return user


# this method will search database by user's numberid .
# returns User
def searchUserByNumberid(nid):
    user = models.User.objects.filter(numberId=nid)
    return user


# the method will check if passed data is correct or not .
# returns JSON with standard response format

def checkForLogin(username, originalPassword):
    theUser = searchUserByUsername(username)
    # password = hashlib.md5(originalPassword.encode()).hexdigest()
    # print(originalPassword)
    password = originalPassword
    if theUser.count() != 1:
        createLog(enums.getDescription(630), str(theUser))
        return {"result": False, "code": 630, "desc": enums.getErrors(630)}
    theUser = theUser[0]
    # print(theUser.encryptedPassword != password)
    if theUser.encryptedPassword != password:
        createLog(enums.getDescription(631), {str(theUser), originalPassword})
        return {"result": False, "code": 631, "desc": enums.getErrors(631)}
    if theUser.banned:
        createLog(enums.getDescription(632), theUser)
        return {"result": False, "code": 632, "desc": enums.getErrors(632)}
    createLog("SuccessFully logedin", str(theUser))
    return {"result": True, "id": theUser.id, "code": 200, "desc": "Login Was Success Fully",
            "token": theUser.token,
            }


# this method will be called whenever we need to login users . it just handle sessions and uses @checkForLogin method .
# returns JSON with standard response format
def doLogin(request):
    if {'username', 'password'}.issubset(request.POST):
        passwrod = hashlib.md5(request.POST['password'].encode()).hexdigest()
        result = checkForLogin(request.POST['username'], passwrod)
        if result['result']:
            request.session['loggedin'] = True
            request.session['token'] = result['token']
        return result
    else:
        createLog("defective data received", request.POST)
        result = {"result": False, "code": 400, "desc": enums.getErrors(400)}
        return result


# this method will check if this user is admin or not .
# returns True and False .
def checkForAdmin(username, password):
    print(checkForLogin(username, password))
    if not checkForLogin(username, password)['result']:
        return False
    # password = hashlib.md5(password.encode()).hexdigest()
    result = models.User.objects.get(userName=username, encryptedPassword=password)
    if not result.isAdmin:
        createLog("User Name with this Username failed to login as admin ", username)
    return result.isAdmin


# this method will returns conductor items within passed time range .
# returns ConductorItem .
def getConductorItem(date):
    items = models.ConductorItem.objects.all().filter(date=date).order_by("startTime")
    return items


# this method will check if passed username and password is belong to an admin or not .
# if belongs , it will insert passed json items .
# returns standard json respond
def insertToConductor(username, password, items):
    if checkForAdmin(username, password):
        for i in items:
            item = items[i]
            splitedTime = item.get("time").split(":")
            splitedDate = item.get("date").split("/")
            date = jdt.datetime(int(splitedDate[0]), int(splitedDate[1]), int(splitedDate[2]), int(splitedTime[0]),
                                int(splitedTime[1]))
            date = date.togregorian()
            newItem = models.ConductorItem(name=item.get("name"), desc=item.get("desc"), startTime=date,
                                           duration=int(item.get("duration")), itemType=item.get("type"))
            try:
                newItem.save()
            except Exception as e:
                createLog("Admin failed to insert new item to conductor", {"error": e, "items": items})
                return {"result": False, "code": 607, "desc": str(e) + enums.getErrors(607)}
        createLog("Admin inserted items to conductor successfully", {"items": items, "admin": username})
        return {"result": True, "code": 200, "desc": "items inserted successfully"}
    else:
        createLog("User with this username tried to insert items to conductor ", {"username": username, "items": items})
        return {"result": False, "code": 666, "desc": enums.getErrors(666)}


# this mehod will find conductor item by id .
# it returns ConductorItem
def getConductorItemById(itemid):
    item = models.ConductorItem.objects.filter(id=itemid)
    return item


def getArchiveItemById(itemid):
    item = models.Archive.objects.filter(id=itemid)
    return item


# this method will edit conductor if passed username and password belongs to an admin .
# it will update database with passed items .
# it returns standard json response
def editConductorItem(username, password, items):
    if checkForAdmin(username, password):
        number = 0
        for i in items:
            item = items[i]
            db_item = getConductorItemById(item.get("id"))
            splitedTime = item.get("time").split(":")
            splitedDate = item.get("date").split("/")
            date = jdt.datetime(int(splitedDate[0]), int(splitedDate[1]), int(splitedDate[2]), int(splitedTime[0]),
                                int(splitedTime[1]))
            date = date.togregorian()
            updatedRows = db_item.update(startTime=date, name=item.get('name'), desc=item.get('desc'),
                                         duration=item.get('duration'), itemType=item.get('type'))
            number = number + updatedRows
        if number == len(items):
            createLog("Admin edited items in conductor successfully", items)
            return {"result": True, "code": 200, "desc": "all items updated successfully"}
        else:
            createLog("Admin failed to update some items in conductor",
                      {"number": str(len(items) - int(number)), "items": items})
            return {"result": True, "code": 608,
                    "desc": str(len(items) - int(number)) + enums.getErrors(608)}
    else:
        createLog("User with this username tried to edit items in conductor ", {"username": username, "items": items})
        return {"result": False, "code": 666, "desc": "User is not admin"}





# this method will read the text file in streaming directory
# returns standard json response
def getUrlTextFile():
    module_dir = os.path.dirname(__file__)
    file_dir = os.path.join(module_dir, "live_url.txt")
    try:
        date_file = open(file_dir, 'r')
        data = date_file.read()
        return {"result": True, "code": 200, "url": data}
    except IOError as e:
        createLog("someone tried to get live url but error occurred", {"error": e})
        return {"result": False, "code": 701, "desc": enums.getErrors(701)}


# this method will write passed url in streaming text file if username and password belong to an admin
# it wil return standard json response
def changeUrlTxtFile(username, password, url):
    if not checkForAdmin(username, password):
        createLog("User with this username tried to change live url", {"username": username, "url": url})
        return {"result": False, "code": 666, "desc": "User is not admin"}

    module_dir = os.path.dirname(__file__)
    file_dir = os.path.join(module_dir, "live_url.txt")
    try:
        data_file = open(file_dir, 'w+')
        data_file.write(url)
        data_file.close()
        createLog("Admin changed live url", {"username": username, "url": url})
        return {"result": True, "code": 200, "desc": "url has been updated"}
    except IOError as e:
        createLog("Admin tried to changed live url but error occurred", {"error": e, "url": url})
        return {"result": False, "code": 701, "desc": enums.getErrors(701)}


def getArchiveItem(size, page):
    startPoint = (int(page) - 1) * int(size)
    endPoint = startPoint + int(size)
    allItems = models.Archive.objects.filter()
    counter = allItems.count()
    items = allItems.order_by('-id')[startPoint:endPoint]
    serilizedArchive = list()
    for item in items:
        thisItem = dict()
        thisItem['id'] = item.id
        thisItem['name'] = item.name
        thisItem['desc'] = item.desc
        thisItem['duration'] = item.duration
        thisItem['photo'] = item.photo.url
        thisItem['itemType'] = item.getType
        thisItem['category'] = item.category
        serilizedArchive.append(thisItem)
    return {"res": serilizedArchive, "counter": counter}


def insertToArchive(username, password, items):
    if checkForAdmin(username, password):
        for i in items:
            item = items[i]
            splitedTime = item.get("time").split(":")
            time = jdt.time(int(splitedTime[0]), int(splitedTime[1]))
            newItem = models.Archive(name=item.get("name"), desc=item.get("desc"), time=time,
                                     duration=int(item.get("duration")), itemType=item.get("type"),
                                     category=item.get("category"), url=item.get("url"))
            try:
                newItem.save()
            except Exception as e:
                createLog("Admin failed to insert new item to archive", {"error": e, "items": items})
                return {"result": False, "code": 607, "desc": str(e) + enums.getErrors(607)}
        createLog("Admin inserted items to conductor successfully", items)
        return {"result": True, "code": 200, "desc": "items inserted successfully"}
    else:
        createLog("User with this username tried to add items to archive ", {"username": username, "items": items})
        return {"result": False, "code": 666, "desc": enums.getErrors(666)}


def editArchiveItem(username, password, items):
    if checkForAdmin(username, password):
        number = 0
        for i in items:
            item = items[i]
            db_item = getArchiveItemById(item.get("id"))
            splitedTime = item.get("time").split(":")
            time = jdt.time(int(splitedTime[0]), int(splitedTime[1]))
            updatedRows = db_item.update(name=item.get("name"), desc=item.get("desc"), time=time,
                                         duration=int(item.get("duration")), itemType=item.get("type"),
                                         category=item.get("category"), url=item.get("url"))
            number = number + updatedRows
        if number == len(items):
            createLog("Admin edited items in archive successfully", items)
            return {"result": True, "code": 200, "desc": "all items updated successfully"}
        else:
            createLog("Admin failed to update some items in archive",
                      {"number": str(len(items) - int(number)), "items": items})
            return {"result": True, "code": 608,
                    "desc": str(len(items) - int(number)) + enums.getErrors(608)}
    else:
        createLog("User with this username tried to edit items in conductor ", {"username": username, "items": items})
        return {"result": False, "code": 666, "desc": "User is not admin"}


def deleteArchiveItem(username, password, items):
    if checkForAdmin(username, password):
        number = 0
        for i in items:
            item = items[i]
            db_item = getArchiveItemById(item.get("id"))
            number = number + db_item.count()
            db_item.delete()
        if len(items) == number and not number == 0:
            createLog("Admin deleted items in conductor successfully", items)
            return {"result": True, "code": 200, "desc": "All items deleted successfully"}
        else:
            if number == 0:
                createLog("Admin failed to delete items in archive",
                          items)
                return {"result": False, "code": 609,
                        "desc": enums.getErrors(609)}
            createLog("Admin failed to delete some items in archive",
                      {"number": str(len(items) - int(number)), "items": items})
            return {"result": False, "code": 610,
                    "desc": str(len(items) - int(number)) + enums.getErrors(610)}
    else:
        createLog("User with this username tried to delete items in archive ", {"username": username, "items": items})
        return {"result": False, "code": 666, "desc": "User is not admin"}


def createTempKey(phone):
    user = searchUserByPhone(phone)
    if user.count() == 1:
        user = user.get()
    else:
        createLog("Phone Number not found for creating Temp Key ( forget Password )", {"phone": phone})
        return False
    user.temp_set.filter().delete()
    # send sms configurations
    date = dt.datetime.now()
    key = hashlib.md5(str(date.timestamp()).encode()).hexdigest()[1:6]
    temp = models.Temp(user=user, key=key, time=date)
    temp.save()
    createLog("new key generated for user", {"key": key, "user": user})
    return True


def updatePassword(key, originalNewPassword):
    newPassword = hashlib.md5(str(originalNewPassword).encode()).hexdigest()
    temp = models.Temp.objects.filter(key=key, done=False)
    if temp.count() != 1:
        createLog("entered key does not match with anyone", {"key": key, "newpassword": originalNewPassword})
        return {"result": False, "code": 902, "desc": "Token is not Correct"}
    temp = temp[0]
    passedTime = temp.time + dt.timedelta(minutes=30)
    user = models.User.objects.filter(id=temp.user.id)
    if dt.datetime.now().time() > passedTime.time():
        createLog("User tried to update password with an obsoleted key", {"user": user, "key": key})
        models.Temp.objects.filter(key=key).update(done=True)
        return {"result": False, "code": 903, "desc": "Token is Expired"}
    if user:
        user = user.update(encryptedPassword=newPassword)
        models.Temp.objects.filter(key=key).update(done=True)
        createLog("user has updated his password with following key", {"user": user, "key": key})
        return {"result": True, "code": 200, "desc": "Password has been changed"}
    else:
        createLog("key found but user didnt found", {"key": key})
        return {"result": False, "code": 904, "desc": "could not change password"}


def changeThisUserDataByUser(request):
    data = json.loads(request.POST['data'])
    if "loggedin" and "token" in request.session:
        operator = models.User.objects.filter(token=request.session['token'])
        if 'userid' in request.POST:
            user = models.User.objects.filter(id=request.POST['userid'])
        else:
            user = operator
        if operator[0] != user[0] and not operator[0].isAdmin:
            createLog("not allowed operator failed to change user data",
                      {"data": data, "user": user, "operator": operator})
            return {"result": False, "code": 667, "error": "you dont have permissions to edit this user data"}
        bDate = data['birthDate'].split("/")
        data['birthDate'] = jdt.datetime(int(bDate[0]), int(bDate[1]), int(bDate[2])).togregorian()
        if 'phone' in data:
            if searchUserByPhone(data['phone']).exists():
                if searchUserByPhone(data['phone'])[0].id != user[0].id:
                    createLog("operator tried to change user data with existing new phone number",
                              {"data": data, "user": user, "operator": operator})
                    return {"result": False, "code": 431, "error": "Phone Number Exists"}
        if 'userName' in data:
            if searchUserByUsername(data['userName']).exists():
                if searchUserByUsername(data['userName'])[0].id != user[0].id:
                    createLog("operator tried to change user data with existing new username",
                              {"data": data, "user": user, "operator": operator})

                    return {"result": False, "code": 430, "error": "Username Exists"}
        if 'numberId' in data:
            if searchUserByNumberid(data['numberId']).exists():
                if searchUserByNumberid(data['numberId'])[0].id != user[0].id:
                    createLog("operator tried to change user data with existing new numberid",
                              {"data": data, "user": user, "operator": operator})
                    return {"result": False, "code": 432, "error": "Number Id exists"}
        kwargs = dict()
        for index in data:
            kwargs[index] = data[index]
        number = user.update(**kwargs)
        if number >= 0:
            result = checkForLogin(data['userName'], user[0].encryptedPassword)
            if result['result']:
                request.session['loggedin'] = True
                createLog("operator changed user data succssfully", {"data": data, "user": user, "operator": operator})
            return {"result": True, "code": 200,
                    "error": str(len(kwargs)) + " items of " + str(number) + " users has been changed",
                    "loginStatus": result}
        else:
            createLog("operator failed to update user data", {"data": data, "user": user, "operator": operator})
            return {"result": False, "code": 1001, "error": "update failed"}
    else:
        createLog("unauthorised user failed to change user data", {"data": data})
        return {"result": False, "code": 667, "error": "please login first"}


def changeThisUserDataByAdmin(request):
    if "loggedin" and "token" in request.session:
        admin = searchUserByUsername(request.POST['username'])
        # user = models.User.objects.filter(id=request.POST['userId'])
        user = models.User.objects.filter(token=request.session['token'])
        data = json.loads(request.POST['data'])
        bDate = data['birthDate'].split("/")
        data['birthDate'] = jdt.datetime(int(bDate[0]), int(bDate[1]), int(bDate[2])).togregorian()
        if 'phone' in data:
            if searchUserByPhone(data['phone']).exists():
                if searchUserByPhone(data['phone'])[0].id != user[0].id:
                    createLog("user tried to change his data with existing new phone number",
                              {"data": data, "user": user, "admin": admin})
                    return {"result": False, "code": 431, "error": "Phone Number Exists"}
        if 'userName' in data:
            if searchUserByUsername(data['userName']).exists():
                if searchUserByUsername(data['userName'])[0].id != user[0].id:
                    createLog("user tried to change his data with existing new username",
                              {"data": data, "user": user, "admin": admin})
                    return {"result": False, "code": 430, "error": "Username Exists"}
        if 'numberId' in data:
            if searchUserByNumberid(data['numberId']).exists():
                if searchUserByNumberid(data['numberId'])[0].id != user[0].id:
                    createLog("user tried to change his data with existing new numberid",
                              {"data": data, "user": user, "admin": admin})
                    return {"result": False, "code": 432, "error": "Number Id exists"}
        kwargs = dict()
        for index in data:
            kwargs[index] = data[index]
        number = user.update(**kwargs)
        if number >= 0:
            createLog("user data has been changed by himself", {"data": data, "user": user, "admin": admin})

            return {"result": True, "code": 200,
                    "error": str(len(kwargs)) + " items of " + str(number) + " users has been changed",
                    "loginStatus": result}
        else:
            createLog("user failed to update his data", {"data": data, "user": user, "admin": admin})

            return {"result": False, "code": 1001, "error": "update failed"}
    else:
        return {"result": False, "code": 667, "error": "please login first"}


def createLog(desc, info):
    logToDatabase(desc, info)
    logToFile(desc, info)


def logToDatabase(desc, info):
    logger = models.Log(desc=desc, info=info)
    try:
        logger.save()
    except Exception as e:
        print(e)


def logToFile(desc, info):
    module_dir = os.path.dirname(__file__)
    file_dir = os.path.join(module_dir, "log.txt")
    try:
        data_file = open(file_dir, mode='a', encoding="utf-8")
    except Exception as e:
        print(e)
        data_file = open(file_dir, mode='w+', encoding="utf-8")
    finally:
        time = dt.datetime.now()
        data = "\n Time : " + str(time) + " , Description : " + desc + " , Informations : " + str(info)
        data_file.write(data)
        data_file.close()
