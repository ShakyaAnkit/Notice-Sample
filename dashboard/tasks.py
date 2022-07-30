import requests
import json

from celery.decorators import periodic_task
from celery.schedules import crontab
from celery import shared_task
from datetime import timedelta

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from dashboard.models import Account, Notice

from .utils import get_notice_api

@shared_task
def get_notice():
    users = User.objects.all()
    for user in users:
        if hasattr(user, 'account'):
            account = user.account
            if account != None and account.api_url != None:
                notice_api = get_notice_api(account)
                if  notice_api:
                    print('Syncing api from {}'.format(account.api_url))
                    notice_sync_id_list = list(Notice.objects.filter(deleted_at__isnull=True, ministry=account.ministry, office=account.office) .values_list('sync_id', flat=True))
                    for notice in notice_api:
                        if Notice.objects.filter(sync_id=notice['id'], ministry=account.ministry, office=account.office, deleted_at__isnull=True).exists():
                            # Updating the notice if notices already exists
                            notice_object = Notice.objects.filter(sync_id=notice['id'], account=account, deleted_at__isnull=True).first()
                            notice_object.account = account
                            notice_object.title = notice['title']
                            notice_object.description = notice['description']
                            notice_object.api_file_url = notice['document_file']
                            notice_object.notice_date = notice['notice_date']
                            # notice_object.office = account.office
                            notice_object.ministry = account.ministry
                            notice_object.link = account.api_url.split('/api')[0] + '/notice/{}'.format(notice['id'])
                            
                            # for future use

                            # if notice['document_file'] != None:
                            #     notice_object.document_file = content_file_from_url(notice['document_file'])

                            notice_object.save(update_fields=['title', 'description', 'api_file_url', 'sync_id', 'notice_date', 'office'])
                        else:
                            # Create a new notices if notice doesnot exist
                            notice_object = Notice(sync_id=notice['id'])
                            notice_object.account = account
                            notice_object.title = notice['title']
                            notice_object.description = notice['description']
                            # notice_object.office = account.office
                            notice_object.ministry = account.ministry
                            notice_object.api_file_url = notice['document_file']
                            notice_object.notice_date = notice['notice_date']
                            notice_object.link = account.api_url.split('/api')[0] + '/notice/{}'.format(notice['id'])

                            # for future use
                            
                            # if notice['document_file'] != None:
                            #     notice_object.document_file = content_file_from_url(notice['document_file'])
                            
                            notice_object.save()

                        # remove sync_id if it exists 
                        if notice['id'] in notice_sync_id_list:
                            notice_sync_id_list.remove(notice['id'])

                    # deleting notices from db
                    Notice.objects.filter(deleted_at__isnull=True, ministry=account.ministry, office=account.office, sync_id__in=notice_sync_id_list).delete()
                    

@periodic_task(run_every=timedelta(minutes=10))
def sync_api():
    get_notice.delay()
    

