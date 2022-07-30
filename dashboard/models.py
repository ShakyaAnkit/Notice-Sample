from jsonfield import JSONField

from django.apps import apps
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from ckeditor.fields import RichTextField

AUDIT_TYPE_CHOICES = (
    (1, 'LOGIN'),
    (2, 'LOGOUT'),
    (3, 'CREATE'),
    (4, 'UPDATE'),
    (5, 'DELETE'),
)

class DateTimeModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        auto_now=False,
    )
    updated_at = models.DateTimeField(
        auto_now_add=False,
        auto_now=True,
    )
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def delete(self, hard=False):
        if not hard:
            self.deleted_at = timezone.now()
            super().save()
        else: 
            super().delete()


# Audit Log which records transactions
class AuditTrail(models.Model):
    modelType = models.CharField('Model Type', max_length=255)
    objectId = models.IntegerField('Model Obj Id')
    action = models.IntegerField(choices=AUDIT_TYPE_CHOICES, default=0, null=False)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    ip = models.GenericIPAddressField(null=True)
    fromObj = JSONField(null=True)
    toObj = JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.modelType) 
    
    def what_is(self):
        return AUDIT_TYPE_CHOICES[self.action - 1][1]

    def what_is_display(self):
        if self.modelType == "User":
            return User.objects.filter(pk=self.objectId).first()
        model = self.modelType.split()
        if len(model) > 1:
            models = model[0]+model[1]
        else:
            models = model[0]
        auditModel = apps.get_model('dashboard', models)
        obj = auditModel.objects.filter(pk=self.objectId).first()
        return obj


class Designation(DateTimeModel):
    name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    gender = models.CharField(max_length=255, choices=(
        ('FEMALE', 'FEMALE'),
        ('MALE', 'MALE'),
        ('OTHERS', 'OTHERS'),
    ))
    date_of_birth = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = 'designation'
        verbose_name_plural = 'designations' 

    def __str__(self):
        return self.name


class Ministry(DateTimeModel):
    name = models.CharField(max_length=255)
    
    class Meta:
        ordering = ["name"]
        verbose_name = 'ministry'
        verbose_name_plural = 'ministries' 

    def __str__(self):
        return self.name

class Office(DateTimeModel):
    ministry = models.ForeignKey(Ministry, related_name='office', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ["name"]
        verbose_name = 'office'
        verbose_name_plural = 'offices' 

    def __str__(self):
        return self.name


class Account(User):
    ministry = models.ForeignKey(Ministry, related_name='account_ministry', verbose_name='Ministry/Office', on_delete=models.CASCADE)
    office = models.ForeignKey(Office, related_name='account_office', on_delete=models.CASCADE, null=True, blank=True)
    api_url = models.CharField(max_length=255, null=True, blank=True)


    class Meta:
        ordering = ["username"]

    def __str__(self):
        return self.username

class Notice(DateTimeModel):
    account = models.ForeignKey(Account, related_name="notice", on_delete=models.CASCADE, null=True, blank=True)
    ministry = models.ForeignKey(Ministry, verbose_name='Ministry/Office', related_name="notice", on_delete=models.CASCADE)
    office = models.ForeignKey(Office, related_name='notice', on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=1024)
    description = RichTextField(null=True, blank=True)
    document_file = models.FileField('File', upload_to='notices', null=True, blank=True)
    notice_date = models.DateField()
    sync_id = models.PositiveIntegerField(null=True, blank=True)
    api_file_url = models.CharField(max_length=1024, null=True, blank=True)
    category = models.ForeignKey('Category', related_name="notice", on_delete=models.CASCADE, null=True, blank=True)
    link = models.URLField(max_length=1024)

    class Meta:
        ordering = ('-notice_date', '-id')

    def __str__(self):
        return self.title
    
    @property
    def has_file(self):
        return self.api_file_url != None or bool(self.document_file)
    
    @property
    def file_url(self):
        if self.api_file_url != None:
            return self.api_file_url
        elif bool(self.document_file):
            return self.document_file.url
        else:
            return None



class Category(DateTimeModel):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ["name"]
        verbose_name = 'category'
        verbose_name_plural = 'categories' 

    def __str__(self):
        return self.name

