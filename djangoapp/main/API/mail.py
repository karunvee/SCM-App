import smtplib
from email.message import EmailMessage
from ..models import *

def send_mail(receiver_mail, request_id, emp_id):

    reqRel = RequestComponentRelation.objects.filter(request__id = request_id)
    content = ''''''
    reqArray = {}
    for reqRelIndex in reqRel:
        reqArray = {
            'id': reqRelIndex.id,
            'component_id' : reqRelIndex.component.pk,
            'component_name' : reqRelIndex.component.name,
            'component_model' : reqRelIndex.component.model,
            'component_machine_type' : reqRelIndex.component.machine_type.name,
            'component_component_type' : reqRelIndex.component.component_type.name,
            'component_image' : reqRelIndex.component.image_url,
            'location' : reqRelIndex.component.location.name,
            'qty' : reqRelIndex.qty,
        }
        content = content + f'''
            <tr>
                <td >
                    <h5 style="text-align: center;">{reqArray['component_name']}</h5>
                </td>
                <td >
                    <h5 style="text-align: center;">{reqArray['qty']} unit.</h5>
                </td>
            </tr>
        '''

    EMAIL_ADDRESS = 'warroom_service@deltaww.com'
    EMAIL_PASSWORD = 'W@rServ1ce'

    msg = EmailMessage()
    msg['Subject'] = f'[ SCM Notify ] Request ID : {request_id}'
    msg['From'] = "warroom_service@deltaww.com"
    msg['To'] = receiver_mail
    # msg['Cc'] = "natsujar@deltaww.com;rapratta@deltaww.com"
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
        <body  bgcolor="#F5F8FA" style=" font-family:Lato, sans-serif; font-size:18px;">
        <div id="email"  style="width: 50%;">
            <table role="presentation" width="50%">
                <tr style="display: flex; align-items: center; justify-content: center; height: 60px;">
                    <td bgcolor="#0086DB" align="center" style="color: white; ">
                        <h3 style="text-align: center; margin-top: 20px;">Spare Part Control Management</h3>
                    </td>
                </tr>
            </table>
            <table role="presentation" bgcolor="#fff"  border="0" cellpadding="0" cellspacing="10px" width="50%" style="padding: 30px 30px 30px 60px;">
                <tr>
                    <td style="
                    display: flex;
                    flex-direction: column;">
                        <h5 style="margin: 0; color: #555555;">Request ID:</h5>
                        <h3 style="background-color: #555555; color: #fff; padding: 5px 10px 5px 10px; text-align: center; margin-top: 5px;">33af9980-8dc5-45fb-9196-ff3d167f9c95</h3>
                        <table width="100%">
                            <tr>
                                <th><h5 style="margin: 0; color: #555555;">Employee ID: </h5></th>
                                <th><h5 style="margin: 0;">TEST</h5></th>
                            </tr>
                            <tr>
                                <th><h5 style="margin: 0; color: #555555;">Name: </h5></th>
                                <th><h5 style="margin: 0;">User.Tester</h5></th>
                            </tr>
                        </table>
                        <hr>
                        <h5 style="margin: 0; color: #555555;">Item List</h5>
                        <table width="100%">
                            {content}
                        </table>
                        <hr>
                        <table width="100%">
                            <tr>
                                <th >
                                    <a align="right" href="https://thwgrwarroom.deltaww.com/scm/approval" style="text-decoration: none; color: #0086DB; border: #ffffff solid 1px; padding: 5px 15px; text-align: center;">
                                        Review
                                    </a>
                                </th>
                                <th >
                                    <a align="right" href="{f"https://thwgrwarroom.deltaww.com:8089/api/request/approved/to/?request_id={request_id}&emp_id={emp_id}"}" style="text-decoration: none; color: #0086DB; border: #0086DB solid 1px; padding: 5px 15px; text-align: center;">
                                        Click to approve
                                    </a>
                                </th>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </div>
        </body>
        </html>
    ''', subtype='html')

    with smtplib.SMTP('deltarelay.deltaww.com', 25) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)