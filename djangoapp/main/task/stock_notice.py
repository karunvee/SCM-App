import os
import django
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangoapp.settings")
django.setup()  # Initialize Django

from django.db.models import F
from django.utils.timezone import now

from main.models import *
from main.serializers import *
from main.API.stock_notice_mail import stock_notice_mail

def main():
    try:
        components = Component.objects.filter(quantity__lt=F('quantity_alert')).order_by('quantity')
        stock_notice_mail('Karun.Wibo@deltaww.com', components)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()
    print("✅ Safety Notice Alert Completed!")