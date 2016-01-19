from celery.task.schedules import crontab
from celery.decorators import periodic_task
from django.core.mail import send_mail
from datetime import datetime
from django.template.loader import render_to_string
from .models import User

def get_receivers( minutes ):
  receivers = []
  for user in User.objects.all():
    if (user.emailEvery == minutes):
      receivers.append(user.email)
  return receivers

def sending_mail( minutes ):
  for user in User.objects.all():
    if (user.emailEvery == minutes):
      if (user.has_messages == True):
        content = "You have new messages"
        user.has_messages = False
        user.save()
      else:
        content = "You have no new messages"
      msg = render_to_string('warcraft/periodic_template.html', {'date': datetime.now(), 'often': minutes, 'name': user.firstName, 'message': content})
      send_mail('Periodic Email', 'nothing', 'chriscraftecs160@gmail.com', [user.email], fail_silently=False, html_message= msg)

@periodic_task(run_every=(crontab(minute='*/10')), name="send_something_1", ignore_result=True)
def send_something_1():
  sending_mail(10)

@periodic_task(run_every=(crontab(minute='*/60')), name="send_something_2", ignore_result=True)
def send_something_2():
  sending_mail(60)