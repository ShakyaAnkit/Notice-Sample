import requests
from io import BytesIO

from django.core import serializers
from django.core.files.base import ContentFile

from .models import AUDIT_TYPE_CHOICES, AuditTrail

AUDIT_CHOICES = {a[1]: a[0] for a in AUDIT_TYPE_CHOICES}

def content_file_from_url(url):
    filename = url.split('/')[-1]
    res = requests.get(url)
    fp = BytesIO()
    fp.write(res.content)
    return ContentFile(fp.getvalue(), filename)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def storeAuditTrail(prevObjModel, objModel, actionType, request):
    aTrail = AuditTrail()
    aTrail.modelType = objModel._meta.verbose_name.title()
    aTrail.objectId = objModel.pk
    aTrail.action = actionType
    aTrail.user = request.user
    aTrail.ip = get_client_ip(request)
    if prevObjModel:
        aTrail.fromObj = serializers.serialize("json", [prevObjModel])
    aTrail.toObj = serializers.serialize("json", [objModel])
    aTrail.save()

def get_notice_api(account):
    try: 
        notices_api = requests.get(account.api_url).json()
    except:
        return None
    return notices_api