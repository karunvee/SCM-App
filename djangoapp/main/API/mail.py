import smtplib
from email.message import EmailMessage
import requests
from ..models import *

def send_mail(approver, requestData):
    EMAIL_ADDRESS = 'warroom_service@deltaww.com'
    EMAIL_PASSWORD = 'W@rRoomServ1ce'

    print('send_mail', approver.email)
    msg = EmailMessage()
    msg['Subject'] = f'[ SCM Notify ] New Request from {requestData.requester_name_center}'
    msg['From'] = EMAIL_ADDRESS

    msg['To'] = approver.email

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
        </tr>
        <tr>
            <td colspan="3" style="height: 1px; background-color: #ababab; margin: 40px 20px;"></td>
        </tr>

    '''
    components = RequestComponentRelation.objects.filter(request__id = requestData.id)

    cid_map = {}

    # Prepare HTML Content First
    for comp in components:
        cid = f'image{comp.component.id}_cid'  # Unique CID for each image
        cid_map[cid] = f'https://thwgrwarroom.deltaww.com:8089/media/{comp.component.image}'
        content += f'''
            <tr>
                <th> 
                   <img src="cid:{cid}" width="80" height="80" style="object-fit: contain; display: block;">
                </th>
                <th> 
                    <h5 style="text-align: center;">{comp.component.name}</h5>
                </th>
                <th>
                    <h5 style="text-align: center; color: #0086DB;">{comp.qty} unit.</h5>
                </th>
            </tr>
        '''

    css_styles = """
    <style type="text/css">
        h1 { font-size: 56px; }
        h2 { font-size: 28px; font-weight: 900; }
        p { font-weight: 100; font-size: 12px; }
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
                    <p style="margin: 0 20px;">New Request Notification</p>
                </td>
            </tr>
        </table>
        <h5>
            Please review the request and approve it if you agree.
        </h5>
        <table>
            <tr>
                <td width="300" valign="middle">
                    <h5 style="margin: 0 20px;">
                    Request ID:
                    </h5>
                </td>
                <td valign="middle">
                    <p style="margin: 0 20px;">
                    {requestData.id}
                    </p>
                </td>
            </tr>
            <tr>
                <td width="300" valign="middle">
                    <h5 style="margin: 0 20px;">
                    Requester account:
                    </h5>
                </td>
                <td valign="middle">
                    <p style="margin: 0 20px;">
                    {requestData.requester}
                    </p>
                </td>
            </tr>
            <tr>
                <td width="300" valign="middle">
                    <h5 style="margin: 0 20px;">
                    Requester name/ID :
                    </h5>
                </td>
                <td valign="middle">
                    <p style="margin: 0 20px;">
                    {requestData.requester_name_center}, {requestData.requester_emp_center}
                    </p>
                </td>
            </tr>
        </table>
        <p style="margin: 0 0 20px 0"></p>
        <table width="100%">
            {content}
        </table>
        <p style="margin: 10px 0 20px 0"></p>
        <table width="100%">
            <tr>
                <td colspan="3" style="height: 1px; background-color: #ababab; margin: 40px 0 0 0;"></td>
            </tr>
            <tr>
                <th width="200">
                    <a align="right" href="https://thwgrwarroom.deltaww.com/scm/approval" style="text-decoration: none; color: #0086DB; border: #ffffff solid 1px; padding: 5px 15px; text-align: center;">
                        Review
                    </a>
                </th>
                <th width="200">
                    <a align="right" href="{f"https://thwgrwarroom.deltaww.com:8089/api/request/approved/to/?request_id={requestData.id}&emp_id={approver.emp_id}"}" style="text-decoration: none; color: #0086DB; padding: 5px 15px; text-align: center;">
                        Approve here
                    </a>
                </th>
            </tr>
            <tr>
                <td colspan="3" style="height: 1px; background-color: #ababab; margin: 40px 0 0 0;"></td>
            </tr>
            <tr>
                <td colspan="3">
                    <h6>
                    Copyright © 2025 - Spare Part Control Management Application - Delta Electronics (Thailand) PCL. (Application Version 1.3.1) - Developed by DET7-AME. 
                    </h6>
                </td>
            </tr>
            <tr>
                <td colspan="3" style="height: 1px; background-color: #ababab; margin: 0 0 40px 0;"></td>
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
    for comp in components:
        image_url = f'https://thwgrwarroom.deltaww.com:8089/media/{comp.component.image}'
        res = requests.get(image_url)

        if res.status_code == 200:
            img_data = res.content
            cid = f'image{comp.component.id}_cid'
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


