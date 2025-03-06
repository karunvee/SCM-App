import os
import django
import sys
import time

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
        apr_list = ApprovedRoute.objects.all()
        for apr in apr_list:
            cc_members = CarbonCopyRoute.objects.filter(approve_route = apr)
            components = Component.objects.filter(location__production_area = apr.production_area, quantity__lt=F('quantity_alert')).order_by('quantity')
            
            cc_members_str = ''

            if cc_members.exists():
                cc_members_str = ','.join([cc_m.member.email for cc_m in cc_members])

            if components.exists():
                stock_notice_mail(apr, cc_members_str, components)

    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()
    print("✅ Safety Notice Alert Completed!")