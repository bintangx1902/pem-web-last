from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.core.exceptions import ObjectDoesNotExist
from os import path, remove
from django.conf import settings


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user', related_query_name='user')
    wa_number = models.CharField('Nomor Whatsapp yang bisa di hubungi', max_length=255)
    nik: str = models.CharField('NIK KTP (Dirahasiakan)', max_length=20)
    is_employee = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} -- {self.wa_number}"

    def get_nik(self):
        return ''.join([itr if idx >= 11 else '*' for idx, itr in enumerate(self.nik)])


class Tools(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}"


class TechnicianJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey('client_side.Complaint', on_delete=models.CASCADE, related_name='job',
                            related_query_name='job')

    def __str__(self):
        return f"{self.user} has job for {self.job.title}"


class GroundReport(models.Model):
    file = models.FileField('upload file bukti lapangan', upload_to='report/')
    case = RichTextField('laporkan kasus yang terjadi di lapangan', config_name='basic')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey('client_side.Complaint', on_delete=models.CASCADE, related_name='job_report',
                            related_query_name='job_report')

    def __str__(self):
        return f"laporan untuk {self.job.title}"

    def delete(self, using=None, keep_parents=False, *args, **kwargs):
        try:
            file_path = path.join(settings.MEDIA_ROOT, self.file.name)
            if path.isfile(file_path):
                remove(file_path)

        except ObjectDoesNotExist as e:
            print(e)

        return super().delete(*args, **kwargs)
