from django.db import models
from django.contrib.auth.models import User
from django.core.validators import *
from company.models import Tools
from ckeditor.fields import RichTextField
import re
need_clean = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')


class Complaint(models.Model):
    title = models.CharField(max_length=255)
    messages = RichTextField(config_name='basic')
    complain = models.ForeignKey(User, on_delete=models.CASCADE)
    feedback = models.IntegerField(default=1, validators=[
        MaxValueValidator(10),
        MinValueValidator(0)
    ])
    address = models.TextField(default="")
    accepted = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    is_done = models.BooleanField(default=False)
    is_open = models.BooleanField(default=False)
    tech_quota = models.IntegerField('Jumlah teknisi yang di butuhkan', default=3)
    due_date = models.DateTimeField(null=True, blank=True)
    cs = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cs', null=True, blank=True)
    ground_price = models.IntegerField(null=True, blank=True)
    stock_price = models.IntegerField(default=30_000, null=True, blank=True)
    tech_price = models.IntegerField(default=20_000, null=True, blank=True)
    total_price = models.IntegerField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    needed_tools = models.ManyToManyField(Tools, null=True, blank=True)
    ticket_code = models.CharField(max_length=32)
    stripe_id = models.CharField(max_length=255, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.complain} -- {self.messages:25}"

    def get_message(self):
        msg = f"{self.messages}"
        msg = re.sub(need_clean, '', msg)
        return f"{msg[:50]} . . . "


class JoinUs(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    foto_ktp = models.ImageField(upload_to='ktp/')
    desc = RichTextField('deskripsikan diri anda !', config_name='basic')
    accepted = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    sent = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.user.username} desc : {self.desc:30}"

    def get_desc(self):
        desc = f"{self.desc}"
        desc = re.sub(need_clean, '', desc)
        return f"{desc[:30]} . . ."
