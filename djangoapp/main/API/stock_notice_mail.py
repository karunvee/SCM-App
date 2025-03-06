import smtplib
from email.message import EmailMessage
import requests
from ..models import *

def stock_notice_mail(receiver, cc_members, data):
    EMAIL_ADDRESS = 'warroom_service@deltaww.com'
    EMAIL_PASSWORD = 'W@rRoomServ1ce'

    print(f'{receiver.production_area.prod_area_name}, {receiver.staff_route.email}, {receiver.supervisor_route.email}, cc to: {cc_members}')
    msg = EmailMessage()
    msg['Subject'] = f'[ SCM Notify ] Safety Stock Notification - Reminder! The quantity of {data.count()} items is below the specified safety stock'
    msg['From'] = EMAIL_ADDRESS

    msg['To'] = f'{receiver.staff_route.email},{receiver.supervisor_route.email}'
    msg['Cc'] = cc_members

    content = '''
        <tr>
            <th> 
                Picture
            </th>
            <th> 
                Equipment Name
            </th>
            <th>
                Quantity
            </th>
            <th>
                Safety Limit
            </th>
        </tr>
        <tr>
            <td colspan="4" style="height: 1px; background-color: #ababab; margin: 40px 20px;"></td>
        </tr>

    '''
    cid_map = {}

    # Prepare HTML Content First
    for equip in data:
        cid = f'image{equip.id}_cid'  # Unique CID for each image
        cid_map[cid] = f'https://thwgrwarroom.deltaww.com:8089/media/{equip.image}'
        content += f'''
            <tr>
                <th> 
                   <img src="cid:{cid}" width="80" height="80" style="object-fit: contain; display: block;">
                </th>
                <th> 
                    <h5 style="text-align: center;">{equip.name}</h5>
                </th>
                <th>
                    <h3 style="text-align: center; color: #d43434;">{equip.quantity} unit.</h3>
                </th>
                <th>
                    <h5 style="text-align: center;">{equip.quantity_alert}</h5>
                </th>
            </tr>
        '''

    css_styles = """
    <style type="text/css">
        h1 { font-size: 56px; }
        h2 { font-size: 28px; font-weight: 900; }
        p { font-weight: 100; }
        td { vertical-align: top; }
        #email { margin: auto; width: 600px; background-color: #fff; }
    </style>
    """

    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        {css_styles}
    </head>
    <body>
        <table>
            <tr>
                <td width="50" valign="middle">
                    <img src="cid:logo_cid" width="50" height="50" style="object-fit: contain; display: block;">
                </td>
                <td valign="middle">
                    <h3 style="margin: 0 20px;">Spare Part Control Management</h3>
                    <p style="margin: 0 20px;">Safety Stock Notification</p>
                </td>
            </tr>
        </table>
        <table style="margin: 0 0 20px 0">
            <tr>
                <td  width="400" valign="middle">
                    <h5>
                        The quantity of  {data.count()}  items is below the specified safety stock
                    </h5>
                </td>
                <td>
                    <a href="https://thwgrwarroom.deltaww.com/scm/storage" 
                    style="display: inline-block; margin: 0 20px; 
                    border-radius: 5px; padding: 8px 20px; text-align: center; text-decoration: underline; font-weight: bold; font-size: 12px;">
                        >> Review <<
                    </a>
                </td>
            </tr>
        </table>
        <h5 style="margin: 0; color: #d43434; margin: 0 0 20px 0;">
            **Please replenish the stock of these equipment as soon as possible**
        </h5>
        <table width="100%">
            {content}
            <tr>
                <td colspan="4" style="height: 1px; background-color: #ababab; margin: 40px 0 0 0;"></td>
            </tr>
            <tr>
                <td colspan="4">
                    <h6>
                    Copyright © 2025 - Spare Part Control Management Application - Delta Electronics (Thailand) PCL. (Application Version 1.3.1) - Developed by DET7-AME. 
                    </h6>
                </td>
            </tr>
            <tr>
                <td colspan="4" style="height: 1px; background-color: #ababab; margin: 0 0 40px 0;"></td>
            </tr>

        </table>

        
    </body>
    </html>
    '''

    # Set HTML content before attaching images
    msg.set_content("Your email client does not support HTML content.")
    msg.add_alternative(html_content, subtype='html')

    # Make the HTML payload "related" once
    msg.get_payload()[1].make_related()

    # Attach images after setting HTML content
    for equip in data:
        image_url = f'https://thwgrwarroom.deltaww.com:8089/media/{equip.image}'
        res = requests.get(image_url)

        if res.status_code == 200:
            img_data = res.content
            cid = f'image{equip.id}_cid'
            msg.get_payload()[1].add_related(img_data, maintype='image', subtype='jpeg', cid=cid)

    logo_url = "https://thwgrwarroom.deltaww.com/static/media/logo-trans.b4bb56d6645e8afa42f4.png"
    res = requests.get(logo_url)
    if res.status_code == 200:
        img_data = res.content
        cid = "logo_cid"
        msg.get_payload()[1].add_related(img_data, maintype='image', subtype='jpeg', cid=cid)

    # Send the email
    with smtplib.SMTP('deltarelay.deltaww.com', 25) as server:
        server.ehlo()
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        print("Email sent successfully!")


