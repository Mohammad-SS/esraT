import datetime
import hashlib
import json
import os
from django.core.files import File
from django.conf import settings as st

from django.shortcuts import render, Http404, get_object_or_404, redirect, HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
import jdatetime as jdt

from streaming import models, functions


# Create your views here.
def logOut(request):
    request.session.flush()
    return redirect("login")


def isLogedIn(req):
    if "token" in req.session:
        req.session.set_expiry(3600)
        return True
    req.session.flush()
    return False


def setSiteSettings(POST):
    arguments = ["tradition2", "tradition1", "sitestatus", "showingItems"]
    if not "tradition2" and "tradition1" and "sitestatus" and "showingItems" in POST:
        raise Http404
    TRsettings = models.Setting.objects.filter(name="todayTradition")
    showingItemSetting = models.Setting.objects.filter(name="LastArchivesToShow")
    siteStatusSetting = models.Setting.objects.filter(name="siteStatus")
    counter = TRsettings.update(value=POST['tradition1'], altValue=POST['tradition2'])
    counter += showingItemSetting.update(value=POST['showingItems'])
    counter += siteStatusSetting.update(value=POST['sitestatus'])
    return JsonResponse({"code": 200, "counter": counter})


def adminLogin(req):
    username = req.POST['username']
    password = req.POST['password']
    password = hashlib.md5(password.encode()).hexdigest()
    user = get_object_or_404(models.User, userName=username, encryptedPassword=password)
    if not user.isAdmin:
        return Http404
    req.session.set_expiry(3600)
    req.session['token'] = user.token
    return JsonResponse({"code": 200, "desc": "admin loged in success fully"})


def deleteConductorItems(request):
    items = json.loads(request.POST['data'])
    for i in items:
        item = items[i]
        db_item = functions.getConductorItemById(item.get("id"))
        db_item.delete()
    return JsonResponse({"code": 200, "desc": "successfully deleted"})


def addNewConductorItemPost(request):
    if "picture" in request.FILES:
        myfile = request.FILES['picture']
    else:
        myfile = None
    spldate = request.POST['date'].split("/")
    spltime = request.POST['startTime'].split(":")
    date = jdt.date(int(spldate[2]), int(spldate[1]), int(spldate[0])).togregorian()
    time = datetime.time(int(spltime[0]), int(spltime[1]))
    time = datetime.datetime.combine(date, time)
    item = models.ConductorItem(name=request.POST['name'],
                                desc=request.POST['desc'],
                                startTime=time,
                                date=date,
                                duration=request.POST['duration'])
    if myfile:
        item.photo = File(myfile)
    item.save()
    if request.POST['meth'] == "submit":
        return redirect("conductor")
    if request.POST['meth'] == "continue":
        return redirect("newCondocturItem")


def editConductorItemPost(request):
    if "picture" in request.FILES:
        myfile = request.FILES['picture']
    else:
        myfile = None
    spldate = request.POST['date'].split("/")
    spltime = request.POST['startTime'].split(":")
    date = jdt.date(int(spldate[2]), int(spldate[1]), int(spldate[0])).togregorian()
    time = datetime.time(int(spltime[0]), int(spltime[1]))
    time = datetime.datetime.combine(date, time)
    item = models.ConductorItem.objects.get(pk=request.POST['itemId'])
    item.startTime = time
    item.date = date
    item.name = request.POST['name']
    item.desc = request.POST['desc']
    item.duration = request.POST['duration']
    if myfile:
        item.photo = File(myfile)
    item.save()
    return redirect("conductor")


def editorDeleteConductorItemPost(request):
    if (request.POST['meth'] == "edit"):
        return editConductorItemPost(request)
    if (request.POST['meth'] == "delete"):
        id = request.POST['itemId']
        db_item = functions.getConductorItemById(id)
        db_item.delete()
        return redirect("conductor")


def addNewArchiveItemPost(request):
    if "picture" in request.FILES:
        picture = request.FILES['picture']
    else:
        picture = None
    file = request.FILES['src']
    file = File(file)
    item = models.Archive(name=request.POST['name'],
                          desc=request.POST['desc'],
                          src=file,
                          category=request.POST['cat'],
                          itemType=request.POST['itemType'],
                          duration=request.POST['duration'])
    if picture:
        item.photo = File(picture)
    item.save()
    if request.POST['meth'] == "submit":
        return redirect("archive")
    if request.POST['meth'] == "continue":
        return redirect("newArchiveItem")


def editArchiveItemPost(request):
    if "picture" in request.FILES:
        picture = request.FILES['picture']
    else:
        picture = None
    item = models.Archive.objects.get(pk=request.POST['itemId'])
    if "file" in request.FILES:
        file = request.FILES['src']
        file = File(file)
        item.src = file
    if picture:
        item.photo = File(picture)
    item.name = request.POST['name']
    item.desc = request.POST['desc']
    item.category = request.POST['cat']
    item.itemType = request.POST['itemType']
    item.duration = request.POST['duration']
    item.save()
    return redirect("archive")


def editorDeleteArchiveItemPost(request):
    if (request.POST['meth'] == "edit"):
        return editArchiveItemPost(request)
    if (request.POST['meth'] == "delete"):
        id = request.POST['itemId']
        db_item = functions.getArchiveItemById(id)
        db_item.delete()
        return redirect("archive")


def deleteArchiveItems(request):
    items = json.loads(request.POST['data'])
    for i in items:
        item = items[i]
        db_item = functions.getArchiveItemById(item.get("id"))
        db_item.delete()
    return JsonResponse({"code": 200, "desc": "successfully deleted"})


def editUserPost(request):
    user = models.User.objects.get(pk=request.POST['itemId'])
    user.fName = request.POST['fName']
    user.lName = request.POST['lName']
    user.numberId = request.POST['numberId']
    user.phone = request.POST['phone']
    splitedDate = request.POST['birthDate'].split("/")
    birthDate = jdt.date(int(splitedDate[2]), int(splitedDate[1]), int(splitedDate[0])).togregorian()
    user.birthDate = birthDate
    user.educationLevel = request.POST['educationLevel']
    if "status" in request.POST:
        if request.POST['status'] == "ban":
            user.isAdmin = False
            user.banned = True
        if request.POST['status'] == "admin":
            user.isAdmin = True
            user.banned = False
        if request.POST['status'] == "regular":
            user.isAdmin = False
            user.banned = False
    user.save()


def editorDeleteUserPost(request):
    if request.POST['meth'] == "edit":
        editUserPost(request)
    if request.POST['meth'] == "delete":
        user = models.User.objects.filter(pk=request.POST['itemId'])
        user.delete()
    return redirect("users")


def postHandler(request):
    handler = request.POST['handler']
    if handler == "login":
        return adminLogin(request)
    token = request.session['token']
    user = functions.searchUserByToken(token)
    if not user[0].isAdmin:
        raise Http404
    else:
        request.session.set_expiry(3600)
    if not 'handler' in request.POST:
        raise Http404
    if handler == "setSettings":
        return setSiteSettings(request.POST)
    if handler == "deleteConductor":
        return deleteConductorItems(request)
    if handler == "deleteArchives":
        return deleteArchiveItems(request)
    if handler == "addNewConductorItem":
        return addNewConductorItemPost(request)
    if handler == "editThisConductorItem":
        return editorDeleteConductorItemPost(request)
    if handler == "addNewArchiveItem":
        return addNewArchiveItemPost(request)
    if handler == "editThisArchiveItem":
        return editorDeleteArchiveItemPost(request)
    if handler == "editThisUser":
        return editorDeleteUserPost(request)

    raise Http404


# Pages :

def conductor(request):
    if not isLogedIn(request):
        return redirect("login")
    if not 'date' in request.GET:
        date = datetime.datetime.now()
    else:
        split = str(request.GET['date']).split("/")
        date = jdt.date(int(split[2]), int(split[1]), int(split[0])).togregorian()
    items = functions.getConductorItem(date)
    context = {"items": items, "date": date.strftime("%Y/%m/%d") , "title" : "کنداکتور"}
    return render(request, 'adminpanel/conductor.html', context)


def addNewConductorItem(request):
    if not isLogedIn(request):
        return redirect("login")
    return render(request, "adminpanel/newCodnductorItem.html" , {"title": "آیتم جدید کنداکتور"})


def editConductorItem(request):
    if not isLogedIn(request):
        return redirect("login")
    item = models.ConductorItem.objects.get(pk=request.GET['id'])
    persianStartTime = item.persianStartTime
    return render(request, "adminpanel/editConductorItem.html", {"item": item, "persianStartTime": persianStartTime})


def login(request):
    if isLogedIn(request):
        return redirect("home")
    return render(request, "adminpanel/login.html" , {"title" : "ورود"})


def homePage(request):
    if not isLogedIn(request):
        return redirect("login")
    title = "صفحه اصلی"
    wUsers = models.User.objects.all()
    admins = wUsers.filter(isAdmin=True)
    sounds = models.Archive.objects.filter(itemType="S")
    soundsTime = 0
    videosTime = 0
    for sound in sounds:
        soundsTime += sound.duration
    videos = models.Archive.objects.filter(itemType="V")
    for video in videos:
        videosTime += video.duration
    context = {"sounds": {"count": sounds.count(), "time": soundsTime},
               "videos": {"count": videos.count(), "time": videosTime},
               "users": {"admin": admins.count(), "regular": wUsers.count()}, "title": title}
    return render(request, "adminpanel/home.html", context)


def settings(request):
    if not isLogedIn(request):
        return redirect("login")
    TRsettings = models.Setting.objects.get(name="todayTradition")
    showingItemSetting = models.Setting.objects.get(name="LastArchivesToShow")
    siteStatusSetting = models.Setting.objects.get(name="siteStatus")
    context = {
        'tradition': TRsettings,
        "showingItem": showingItemSetting,
        "siteStatus": siteStatusSetting,
        "title": "تنظیمات"
    }
    return render(request, "adminpanel/settings.html", context)


def archive(request):
    if not isLogedIn(request):
        return redirect("login")
    if 'page' in request.GET:
        page = request.GET['page']
    else:
        page = 1
    items = functions.getArchiveItem(20, page)
    last_page = items.get('counter')
    last_page = int(last_page / 20) + 1
    pages = range(1, last_page + 1)
    context = {"items": items.get('res'), "pages": pages, "current_page": int(page) , "title" : "آرشیو"}
    return render(request, 'adminpanel/archive.html', context)


def editArchiveItem(request):
    if not isLogedIn(request):
        return redirect("login")
    item = models.Archive.objects.get(pk=request.GET['id'])
    item.addTime = jdt.datetime.fromgregorian(datetime=item.addTime).strftime("%H:%M - %Y/%m/%d")
    item.size = str(int(item.src.size / 1000) / 1000) + " مگابایت"
    return render(request, "adminpanel/editArchiveItem.html", {"item": item , "title" : "ویرایش آیتم"})


def addNewArchiveItem(request):
    if not isLogedIn(request):
        return redirect("login")
    return render(request, "adminpanel/newArchiveItem.html" , {"title" : "آیتم جدید"})


def users(request):
    if not isLogedIn(request):
        return redirect("login")
    if "page" in request.GET:
        page = request.GET['page']
    else:
        page = 1

    counter = models.User.objects.all()
    startPoint = (int(page) - 1) * 10
    endPoint = startPoint + 10
    last_page = int(counter.count() / 10) + 1
    pages = range(1, last_page + 1)
    items = models.User.objects.filter().order_by("registerTime")[startPoint:endPoint]
    self = counter.get(token=request.session['token']).pk
    return render(request, "adminpanel/users.html",
                  {"items": items, "selfId": self, "pages": pages, "current_page": int(page) , "title" : " کاربران"})


def editUser(request):
    if not isLogedIn(request):
        return redirect("login")
    item = models.User.objects.get(pk=request.GET['id'])
    isself = item.token == request.session['token']
    item.registerTime = jdt.datetime.fromgregorian(datetime=item.registerTime).strftime("%H:%M - %Y/%m/%d")
    return render(request, "adminpanel/editUser.html", {"item": item, "isself": isself , "title" : "ویرایش کاربر"})
