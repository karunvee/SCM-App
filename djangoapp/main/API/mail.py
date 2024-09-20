import smtplib
from email.message import EmailMessage
from ..models import *

def send_mail(receiver_mail, request_id, emp_id, request_emp_id, requester_name):

    reqRel = RequestComponentRelation.objects.filter(request__id = request_id)
    content = ''''''

    for reqRelIndex in reqRel:
        content = content + f'''
            <tr>
                <th> 
                    <h5 style="text-align: center;">{reqRelIndex.component.name}</h5>
                </th>
                <th>
                    <h5 style="text-align: center;">{reqRelIndex.qty} unit.</h5>
                </th>
            </tr>
        '''

    EMAIL_ADDRESS = 'warroom_service@deltaww.com'
    EMAIL_PASSWORD = 'W@rRoomServ1ce'

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
        <body style="font-family:Lato, sans-serif; font-size:18px; padding: 40px 15px; background-color: #aadeff; height: fit-content">
        <table id="email"  style="width: 100%; background-color: #fff;" cellspacing="10">
            <table role="presentation" style="width: 100%; background-color: #fff;">
                <tr style="display: flex; align-items: center; justify-content: center; height: 60px;">
                    <td align="center" style="color: #0086DB; ">
                        <h3 style="text-align: center; margin-top: 20px;">Spare Part Control Management</h3>
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
                                    <h5 style="text-align: center;">{request_id}</h5>
                                </th>
                            </tr>
                            <tr>
                                <th>
                                    <h5 style="text-align: center;">Employee ID: </h5>
                                </th>
                                <th>
                                    <h5 style="text-align: center;">{request_emp_id}</h5>
                                </th>
                            </tr>
                            <tr>
                                <th>
                                    <h5 style="text-align: center;">Name </h5>
                                </th>
                                <th>
                                    <h5 style="text-align: center;">{requester_name}</h5>
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
                                    <a align="right" href="https://thwgrwarroom.deltaww.com/scm/approval" style="text-decoration: none; color: #0086DB; border: #ffffff solid 1px; padding: 5px 15px; text-align: center;">
                                        Review
                                    </a>
                                </th>
                                <th >
                                    <a align="right" href="{f"https://thwgrwarroom.deltaww.com:8089/api/request/approved/to/?request_id={request_id}&emp_id={emp_id}"}" style="text-decoration: none; color: #0086DB; padding: 5px 15px; text-align: center;">
                                         >> Approve here <<
                                    </a>
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

