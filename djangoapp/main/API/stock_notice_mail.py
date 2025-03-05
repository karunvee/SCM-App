import smtplib
from email.message import EmailMessage
import requests
from ..models import *

def stock_notice_mail(receiver_mail, data):

    EMAIL_ADDRESS = 'warroom_service@deltaww.com'
    EMAIL_PASSWORD = 'W@rRoomServ1ce'

    msg = EmailMessage()
    msg['Subject'] = f'[ SCM Notify ] Receiver Email : {receiver_mail}'
    msg['From'] = "warroom_service@deltaww.com"
    msg['To'] = receiver_mail
    # msg['Cc'] = "natsujar@deltaww.com;"
    
    content = ''''''
    cid_map = {}
    for equip in data:

        res = requests.get(f'https://thwgrwarroom.deltaww.com:8089/media/{equip.image}')
        if res.status_code == 200:
            img_data = res.content
            cid = f'image{equip.id}_cid'  # Unique CID for each image
            cid_map[cid] = f'https://thwgrwarroom.deltaww.com:8089/media/{equip.image}'

            # Attach the image to the email with a unique CID
            msg.get_payload()[0].add_related(img_data, 'image', 'jpeg', cid=cid)

        content = content + f'''
            <tr>
                <th> 
                    <img src="cid:image{equip.id}_cid">
                </th>
                <th> 
                    <h5 style="text-align: center;">{equip.name}</h5>
                </th>
                <th>
                    <h5 style="text-align: center;">{equip.quantity} unit.</h5>
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

    msg.set_content(f'''
        <!DOCTYPE html>
        <html>
        <head>
            <link rel="stylesheet" type="text/css" hs-webfonts="true" href="https://fonts.googleapis.com/css?family=Lato|Lato:i,b,bi">
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            {css_styles}
        </head>
        <body style="font-family:Lato, sans-serif; font-size:18px; padding: 40px 15px; background-color: #aadeff; height: fit-content">
        <table id="email"  style="width: 100%; background-color: #fff;" cellspacing="10">
            <table role="presentation" style="width: 100%; background-color: #fff;">
                <tr style="display: flex; align-items: center; justify-content: flex-start; height: 60px;">
                    <td align="center" style="color: #d43434; ">
                        <h3 style="text-align: center; margin-top: 20px;">
                        Spare Part Control Management
                        </h3>
                    </td>
                </tr>
            </table>
            <table role="presentation" bgcolor="#fff"  border="0" width="100%" style="PADDING: 30px;">
                <tr>
                    <td style="
                    display: flex;
                    flex-direction: column;">
                        <h5 style="margin: 0; color: #555555; text-decoration: underline;">Requester Information</h5>
                        <table width="100%" style="text-align: center; MARGIN-BOTTOM: 30px;">
                            <tr>
                                <th>
                                    <h5 style="text-align: center;">Request ID: </h5>
                                </th>
                                <th>
                                    <h5 style="text-align: center;">{'None'}</h5>
                                </th>
                            </tr>
                            <tr>
                                <th>
                                    <h5 style="text-align: center;">Employee ID: </h5>
                                </th>
                                <th>
                                    <h5 style="text-align: center;">{'None'}</h5>
                                </th>
                            </tr>
                            <tr>
                                <th>
                                    <h5 style="text-align: center;">Name </h5>
                                </th>
                                <th>
                                    <h5 style="text-align: center;">{'None'}</h5>
                                </th>
                            </tr>
                        </table>
                        <h5 style="margin: 0; color: #555555; text-decoration: underline;">Item List</h5>
                        <table width="100%" style="MARGIN-TOP: 30px">
                            {content}
                        </table>
                        <hr>
                        <table width="100%">
                            <tr>
                                <th >
                                    <a align="right" href="https://thwgrwarroom.deltaww.com/scm/storage" style="text-decoration: none; color: #0086DB; border: #ffffff solid 1px; padding: 5px 15px; text-align: center;">
                                        Review
                                    </a>
                                </th>
                                <th >
                        
                                </th>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </table>
        </body>
        </html>
    ''', subtype='html')

    with smtplib.SMTP('deltarelay.deltaww.com', 25) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

