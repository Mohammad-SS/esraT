from django.db import models
from django_jalali.db import models as jmodel
import datetime
import jdatetime
from django.conf import settings
from django.utils import timezone


class User(models.Model):
    userName = models.CharField(max_length=18, verbose_name="User Name")
    encryptedPassword = models.CharField(
        max_length=32, verbose_name="MD5 Hashed Password")
    fName = models.CharField(max_length=15, verbose_name="First Name")
    lName = models.CharField(max_length=15, verbose_name="Last Name")
    phone = models.CharField(max_length=11, verbose_name="Phone Number")
    numberId = models.CharField(max_length=10, verbose_name="Number ID")
    birthDate = models.DateField(
        auto_now=False, auto_now_add=False, verbose_name="Birth Date", default=None)
    educationLevel = models.CharField(
        max_length=15, verbose_name="Education Level", default=None)
    registerTime = models.DateTimeField(
        verbose_name="Register Date and Time")
    isAdmin = models.BooleanField(
        default=False, verbose_name="Is This User Admin ?")
    banned = models.BooleanField(
        default=False, verbose_name="Is This User Banned ?")
    token = models.CharField(max_length=32)

    def __str__(self):
        return (self.userName)
    @property
    def persianBirthDate(self):
        pst = jdatetime.datetime.fromgregorian(datetime=self.birthDate).strftime("%d/%m/%Y")
        return pst

class ConductorItem(models.Model):
    name = models.CharField(max_length=30, verbose_name="Item Name")
    desc = models.TextField(verbose_name="Description")
    startTime = models.DateTimeField(auto_now=False, auto_now_add=False, verbose_name="Start Air Time")
    photo = models.ImageField(upload_to='ConductorImages', default='default.jpeg', blank=True, null=True)
    date = models.DateField(verbose_name="Date")
    duration = models.IntegerField(verbose_name="Program Duration")

    def __str__(self):
        return self.name

    @property
    def persianStartTime(self):
        pst = jdatetime.datetime.fromgregorian(datetime=self.startTime).strftime("%H:%M")
        return pst

    @property
    def persianDate(self):
        pd = jdatetime.datetime.fromgregorian(datetime=self.date).strftime("%Y/%m/%d")
        return pd

    @property
    def endTime(self):
        endTime = self.startTime + datetime.timedelta(minutes=self.duration)
        return endTime


class Archive(models.Model):
    ITEM_TYPE = (('S', 'صوتی'), ('V', 'تصویری'))
    name = models.CharField(max_length=50, verbose_name="Item Name")
    desc = models.TextField(verbose_name="Description")
    duration = models.IntegerField(verbose_name="Duration of this item", default="120")
    url = models.URLField(max_length=200, verbose_name="URL", default=settings.BASE_URL, blank=True)
    photo = models.ImageField(upload_to='ArchiveImages', default='default.jpeg', blank=True, null=True)
    src = models.FileField(upload_to='ArchiveFiles')
    itemType = models.CharField(
        max_length=1, choices=ITEM_TYPE, verbose_name="Type of This Item")
    category = models.CharField(max_length=35)
    addTime = models.DateTimeField(auto_now=True)

    @property
    def getType(self):
        if self.itemType == 'V':
            return "تصویری"
        elif self.itemType == 'S':
            return "صوتی"
        else:
            return 'آرشیو'

    def __str__(self):
        return self.name


class Temp(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    time = models.DateTimeField()
    key = models.CharField(max_length=20)
    done = models.BooleanField(default=False)


class Log(models.Model):
    time = models.TimeField(auto_now=True)
    desc = models.TextField()
    info = models.TextField()


class Attachment(models.Model):
    type = models.CharField(max_length=5)
    uri = models.URLField()
    user = models.OneToOneField("User", on_delete=models.CASCADE, related_name="avatar")


class Setting(models.Model):
    name = models.CharField(max_length=45)
    value = models.CharField(max_length=500)
    altValue = models.CharField(max_length=500, default=None, null=True, blank=True)
    type = models.CharField(max_length=30)
    hasTwoVals = models.BooleanField(default=False)

    def __str__(self):
        return self.name
