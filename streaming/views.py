from django.shortcuts import render, HttpResponse
from django.http import HttpResponse, JsonResponse , Http404
from json import JSONEncoder
from django.views.decorators.csrf import csrf_exempt
from streaming import models, functions, enums
import datetime
import json
import jdatetime as jdt
from django.utils.encoding import smart_str
from django.conf import settings
import os
import datetime as dt
from django.db.models import Q , Case , When


# this View will be called when /register/ url comes up . Required data for register user :
# userName : @string . length <= 18
# password : @string . it will be hashed by MD5 and hexa decimal
# fName & lName : @string . length <= 15
# phone : @string . length <=11
# numberId : @string . length <=10
# birthDate : @date . it must be in jalali format . it will be converted to gregorian before save to db . xxxx/xx/xx
# educationLevel : @string .length<=15
@csrf_exempt
def registerNewUser(request):
    data_received = None
    # First Check if all arguments is passed by POST data .
    if {'username', 'password', 'fname', 'lname', 'phone', 'numberid', 'birthdate', 'educationlvl'}.issubset(
            request.POST):
        data_received = {"username": smart_str(request.POST['username']), "password": request.POST['password'],
                         "fname": request.POST['fname'],
                         "lname": request.POST['lname'], "nid": request.POST['numberid'],
                         "birthdate": request.POST['birthdate'], "edlvl": request.POST['educationlvl'],
                         'phone': request.POST['phone']}
    else:
        # if its not passed , so give 404 code
        functions.createLog("one user trying to signup , but defective defective", {"data": request.POST})
        jsonResponder = {"result": False, "code": 400,
                         "desc": "defective data received"}

    if data_received is not None:
        signUpRes = functions.signUP(data_received)
        if signUpRes['result']:
            request.session['loggedin'] = True
            request.session['token'] = signUpRes['token']
        jsonResponder = signUpRes

    return JsonResponse(jsonResponder, JSONEncoder, safe=False)


@csrf_exempt
def loginUsers(request):
    return JsonResponse(functions.doLogin(request), JSONEncoder, safe=False)


@csrf_exempt
def logOut(request):
    if 'loggedin' not in request.session:
        functions.createLog("user tried to logout , but not logged in before", {"data": request.POST})
        return JsonResponse({"result": False, "code": 404, "desc": "You are not loggedin"}, JSONEncoder)
    try:
        user = functions.searchUserByToken(request.session['token'])
        request.session.flush()
        functions.createLog("user signed out", {"user": user})
        return JsonResponse({"result": True, "code": 200, "desc": "You have Logged Out Success Fully"}, JSONEncoder)
    except KeyError:
        pass


@csrf_exempt
def showConductor(request):
    if 'date' in request.GET:
        split = str(request.GET['date']).split("/")
    else:
        return JsonResponse({"result": False, "code": 620, "desc": "No date received"}, JSONEncoder)
    date = datetime.datetime(int(split[2]), int(split[1]), int(split[0]))
    items = functions.getConductorItem(date)
    serilizedConductor = list()
    for item in items:
        thisItem = dict()
        thisItem['name'] = item.name
        thisItem['desc'] = item.desc
        thisItem['duration'] = item.duration
        thisItem['persianStartTime'] = item.persianStartTime
        thisItem['photo'] = item.photo.url
        thisItem['persianDate'] = item.persianDate
        thisItem['endTime'] = item.endTime.strftime("%H:%M")
        if dt.datetime.now().time() < item.endTime.time():
            thisItem['isNow'] = True
        serilizedConductor.append(thisItem)
    return JsonResponse({"result": True, "code": 200, "items": serilizedConductor, 'date': date.strftime('%Y/%m/%d')},
                        JSONEncoder, safe=False)


@csrf_exempt
def addNewItemToConductor(request):
    # username = request.POST['username']
    # password = request.POST['password']
    user = models.User.objects.get(token=request.session['token'])
    items = json.loads(request.POST['data'])
    jsonResponder = functions.insertToConductor(user.userName, user.encryptedPassword, items)
    return JsonResponse(jsonResponder, JSONEncoder, safe=False)


def insertfake(request):
    for i in range(0, 30):
        name = "آیتم شماره" + str(i)
        desc = "یک آیتم فیک الکی"
        item = models.ConductorItem(name=name, desc=desc, duration=2, startTime=datetime.datetime.now(),
                                    date=datetime.datetime.now())
        item.save()
    return HttpResponse("DONE")


@csrf_exempt
def editThisConductorItem(request):
    # username = request.POST['username']
    # password = request.POST['password']
    user = models.User.objects.get(token=request.session['token'])
    items = json.loads(request.POST['data'])
    jsonResponder = functions.editConductorItem(user.userName, user.encryptedPassword, items)
    return JsonResponse(jsonResponder, JSONEncoder, safe=False)


@csrf_exempt
def deleteThisConductorItem(request):
    user = models.User.objects.get(token=request.session['token'])
    items = json.loads(request.POST['data'])
    jsonResponder = functions.deleteConductorItem(user.userName, user.encryptedPassword, items)
    return JsonResponse(jsonResponder, JSONEncoder, safe=False)


@csrf_exempt
def showLive(request):
    jsonResponder = functions.getUrlTextFile()
    return JsonResponse(jsonResponder, JSONEncoder, safe=False)


@csrf_exempt
def changeLiveUrl(request):
    # username = request.POST['username']
    # password = request.POST['password']
    url = request.POST['url']
    user = models.User.objects.get(token=request.session['token'])
    jsonResponder = functions.changeUrlTxtFile(user.userName, user.encryptedPassword, url)
    return JsonResponse(jsonResponder, JSONEncoder)


@csrf_exempt
def showArchive(request):
    if 'page' not in request.POST:
        page = 1
    else:
        page = request.POST['page']
    print(request.POST['page'])
    size = 6
    result = functions.getArchiveItem(size, page)
    lastPage = int(result['counter'] / size) + 1
    return JsonResponse({"result": True, "code": 200, "items": result['res'] , "lastPage" : lastPage}, JSONEncoder, safe=False)


@csrf_exempt
def addNewItemToArchive(request):
    # username = request.POST['username']
    # password = request.POST['password']
    items = json.loads(request.POST['data'])
    user = models.User.objects.get(token=request.session['token'])
    jsonResponder = functions.insertToArchive(user.userName, user.encryptedPassword, items)
    return JsonResponse(jsonResponder, JSONEncoder, safe=False)


@csrf_exempt
def editThisArchiveItem(request):
    # username = request.POST['username']
    # password = request.POST['password']
    items = json.loads(request.POST['data'])
    user = models.User.objects.get(token=request.session['token'])
    jsonResponder = functions.editArchiveItem(user.userName, user.encryptedPassword, items)
    return JsonResponse(jsonResponder, JSONEncoder, safe=False)


@csrf_exempt
def deleteThisArchiveItem(request):
    # username = request.POST['username']
    # password = request.POST['password']
    items = json.loads(request.POST['data'])
    user = models.User.objects.get(token=request.session['token'])
    jsonResponder = functions.deleteArchiveItem(user.userName, user.encryptedPassword, items)
    return JsonResponse(jsonResponder, JSONEncoder, safe=False)


@csrf_exempt
def forgetPassword(request):
    phone = request.POST['phone']
    result = functions.createTempKey(phone)
    if result:
        return JsonResponse({"result": True, "code": 200, "desc": "Code has been sent successfully"}, JSONEncoder,
                            safe=False)
    else:
        return JsonResponse({"result": False, "code": 909, "desc": "Could not send Code , Phone Number Not Found"}, JSONEncoder, safe=False)


@csrf_exempt
def changePassword(request):
    key = request.POST['key']
    newPassword = request.POST['password']
    result = functions.updatePassword(key, newPassword)
    return JsonResponse(result, JSONEncoder, safe=False)


@csrf_exempt
def changeUserDataByUser(request):
    print(request.POST)
    result = functions.changeThisUserDataByUser(request)
    return JsonResponse(result, JSONEncoder, safe=False)


@csrf_exempt
def changeUserDataByAdmin(request):
    result = functions.changeThisUserDataByAdmin(request)
    return JsonResponse(result, JSONEncoder, safe=False)


@csrf_exempt
def deleteAccountByUser(request):
    # print(result)
    if "loggedin" and "token" in request.session:
        operator = models.User.objects.filter(token=request.session['token'])
        if 'userid' in request.POST:
            user = models.User.objects.filter(id=request.POST['userid'])
            if user.count() != 1:
                functions.createLog("deleting operation failed beqause user didnt found",
                                    {"userid": request.POST['userid'], "operator": operator})
                return JsonResponse({"result": False, "desc": "user didnt found", "code": 698},
                                    JSONEncoder)
        else:
            user = operator
        if operator[0] != user[0] and not operator[0].isAdmin:
            functions.createLog("not allowed operator failed to delete user", {"user": user, "operator": operator})
            return JsonResponse(
                {"result": False, "code": 667, "error": "you dont have permissions to delete this user"}, JSONEncoder)
        if operator[0].isAdmin and operator[0] == user[0]:
            functions.createLog("admin tried to delete his self . this is only possible from database",
                                {"admin": operator})
            return JsonResponse(
                {"result": False, "code": 697, "error": "you dont have permissions to delete this user"}, JSONEncoder)

        try:
            user.delete()
            functions.createLog("user has been deleted user successfully", {"user": user, "operator": operator})
            return JsonResponse({"result": True, "desc": "Account Has been deleted success fully", "code": 200},
                                JSONEncoder)
        except Exception as e:
            functions.createLog("something went wrong when operator tried to delete user",
                                {"user": user, "operator": operator, "error": e})
            return JsonResponse(
                {"result": True, "desc": "something went wrong when operator tried to delete user", "code": 200,
                 "error": e}, JSONEncoder)

    else:
        return JsonResponse({"result": False, "desc": "Could not delete account", "code": 1003}, JSONEncoder)


@csrf_exempt
def deleteAccountByAdmin(request):
    result = functions.checkForAdmin(request.POST['username'], request.POST['password'])
    # print(result)
    if result:
        user = models.User.objects.filter(id=request.POST['userId'])
        user.delete()
        return JsonResponse({"result": True, "desc": "This Account Has been deleted success fully", "code": 200},
                            JSONEncoder)
    else:
        return JsonResponse({"result": False, "desc": "Could not delete account", "code": 1003}, JSONEncoder)


@csrf_exempt
def getUserData(request):
    user = models.User.objects.get(token=request.session['token'])
    birthDate = jdt.datetime.fromgregorian(datetime=user.birthDate).strftime("%Y/%m/%d")
    registerTime = jdt.datetime.fromgregorian(datetime=user.registerTime).strftime("%Y/%m/%d")
    jsonResponder = {"code": 200, "desc": "data recived successfully",
                     "data": {"userName": user.userName, "ID": user.id, "firstName": user.fName, "lastName": user.lName,
                              "phone": user.phone, "numberId": user.numberId, "birthDate": birthDate,
                              "educationLevel": user.educationLevel, "registerTime": registerTime, }}
    return JsonResponse(jsonResponder, JSONEncoder)


@csrf_exempt
def getAllUsers(request):
    operator = models.User.objects.get(token=request.session['token'])
    if not operator.isAdmin:
        functions.createLog("not allowed operator failed to get users list", {"user": operator})
        return JsonResponse(
            {"result": False, "code": 666, "error": "you dont have permissions"}, JSONEncoder)
    else:
        users = list(models.User.objects.filter().all().values('userName', 'id', 'numberId', 'phone'))
        return JsonResponse(
            {"result": True, "code": 200, "data": users}, JSONEncoder)

def logout(request):
    request.session.flush()
    return JsonResponse({'code': 999}, JSONEncoder)

def checkLogin(request , token):
    if not 'token' in request.session:
        return False
    else:
        if not request.session['token'] == token :
            return False
        else:
            request.session.set_expiry(0)
            return True

@csrf_exempt
def getHomePage(request):
    token = request.POST['token']
    print(request.session.get_expiry_age())
    if not checkLogin(request , token):
        return logout(request)

    token = models.User.objects.filter(token=token)
    if not token.exists() or token[0].banned:
        return logout(request)
    tradition = models.Setting.objects.get(name='todayTradition')

    todayConductor = models.ConductorItem.objects.filter(date=dt.datetime.now())
    serilizedConductor = list()
    for item in todayConductor:
        thisItem = dict()
        thisItem['ID'] = item.id
        thisItem['name'] = item.name
        thisItem['desc'] = item.desc
        thisItem['duration'] = item.duration
        thisItem['persianStartTime'] = item.persianStartTime
        thisItem['photo'] = item.photo.url
        thisItem['persianDate'] = item.persianDate
        thisItem['endTime'] = item.endTime.strftime("%H:%M")
        if dt.datetime.now().time() < item.endTime.time():
            thisItem['isNow'] = True
        print(thisItem)
        serilizedConductor.append(thisItem)
    # Archive
    number = int(models.Setting.objects.get(name='LastArchivesToShow').value)
    lastArchiveItems = models.Archive.objects.filter().order_by('-id')[:number]
    # print(lastArchiveItems)
    serilizedArchive = list()
    for item in lastArchiveItems:
        thisItem = dict()
        thisItem['ID'] = item.id
        thisItem['name'] = item.name
        thisItem['desc'] = item.desc
        thisItem['duration'] = item.duration
        thisItem['photo'] = item.photo.url
        thisItem['itemType'] = item.getType
        thisItem['category'] = item.category
        thisItem['address'] = item.url
        thisItem['src'] = item.src.url

        serilizedArchive.append(thisItem)

    return JsonResponse({'code': 200, 'conductorItems': serilizedConductor, 'archiveList': serilizedArchive,
                         'tradition': {'arabic': tradition.value, 'persian': tradition.altValue}}, JSONEncoder)


def checkConnection(request):
    return HttpResponse(True)


@csrf_exempt
def showNewArchive(request):
    newSounds = models.Archive.objects.filter(itemType="S").order_by('-id')[:6]
    serilizedSounds = list()
    for item in newSounds:
        thisItem = dict()
        thisItem['name'] = item.name
        thisItem['desc'] = item.desc
        thisItem['duration'] = item.duration
        thisItem['photo'] = item.photo.url
        thisItem['itemType'] = item.getType
        thisItem['category'] = item.category
        thisItem['address'] = item.url
        thisItem['src'] = item.src.url


        serilizedSounds.append(thisItem)
    newVideos = models.Archive.objects.filter(itemType="V").order_by('-id')[:6]
    serilizedVideos = list()
    for item in newVideos:
        thisItem = dict()
        thisItem['name'] = item.name
        thisItem['desc'] = item.desc
        thisItem['duration'] = item.duration
        thisItem['photo'] = item.photo.url
        thisItem['itemType'] = item.getType
        thisItem['category'] = item.category
        thisItem['address'] = item.url
        thisItem['src'] = item.src.url


        serilizedVideos.append(thisItem)
    return JsonResponse({'code': 200, 'newSounds': serilizedSounds, 'newVideos': serilizedVideos}, JSONEncoder)

@csrf_exempt
def searchInArchive(request):
    sound = request.POST['sound']
    video = request.POST['video']
    sort = int(request.POST['sort'])
    if(sort == 1):
        sort = "-addTime"
    if (sort == 0):
        sort = "-duration"
    if (sort == 2):
        sort = "addTime"
    if sound=="true" and video=="true":
        typeQuery = Q()
    elif sound=="true" and not video=="true" :
        typeQuery = Q(itemType="S")
    elif video=="true" and not sound=="true":
        typeQuery = Q(itemType="V")

    string = request.POST['string']
    if string:
        stringQuery = Q(Q(category__contains=string) | Q(name__contains=string))
    else:
        stringQuery = Q()
    items = models.Archive.objects.filter(typeQuery).filter(stringQuery).order_by(sort)
    print(items)
    serilizedArchive = list()
    for item in items:
        thisItem = dict()
        thisItem['name'] = item.name
        thisItem['desc'] = item.desc
        thisItem['duration'] = item.duration
        thisItem['photo'] = item.photo.url
        thisItem['itemType'] = item.getType
        thisItem['category'] = item.category
        serilizedArchive.append(thisItem)

    return JsonResponse({'code': 200, 'searchResult': serilizedArchive}, JSONEncoder)


def downloadItemById(request , id):
    item = models.Archive.objects.get(id=id)
    file_path = os.path.join(settings.MEDIA_ROOT, item.src.name)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="video/x-msvideo")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404
