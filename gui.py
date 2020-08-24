# Copyright IBM Corp. 2016 All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import PySimpleGUI as sg
import sys
import requests
import json
import random


sg.theme('Material1')

first_factor_password = "Passw0rd"
secret_file = "secrets.json"
with open(secret_file, "r") as f:
    data = json.load(f)
client_id = data["client_id"]
client_secret = data["client_secret"]
tenant = data["tenant"]

def get_options(username):
    global access_token
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = {
      'grant_type': 'client_credentials',
      'client_id': client_id,
      'client_secret': client_secret,
      'scope': 'openid'
    }
    
    link = "https://"+tenant+"/v1.0/endpoint/default/token"
    response = requests.post(link, headers=headers,data=data)
    response_dict = json.loads(response.text)
    access_token = response_dict["access_token"]
    headers = {
        'Authorization': 'Bearer '+access_token,
        'Content-type': 'application/scim+json',
        'Accept': 'application/scim+json',
    }
    
    params = (
        ('filter', f'userName eq "{username}"'),
    )
    link = 'https://'+tenant+'/v2.0/Users'
    response = requests.get(link, headers=headers, params=params)
    response_dict = json.loads(response.text)
    email = response_dict["Resources"][0]["emails"][0]["value"]
    mobile = response_dict["Resources"][0]["phoneNumbers"][0]["value"]
    owner = response_dict["Resources"][0]["id"]
    #print(f"\nfetched email for user {username} is {email}")
    #print(f"fetched number for user {username} is {mobile}")
    return email,mobile,owner
    

def send_otp(email,owner):
    headers = {
        'Authorization': 'Bearer '+access_token,
        'Content-type': 'application/json',
        'Accept': 'application/json',
    }
    link = 'https://'+tenant+'/v2.0/factors/emailotp'
    response = requests.get(link, headers=headers)
    response_dict = json.loads(response.text)

    for dict1 in response_dict["emailotp"]:
        if dict1["userId"] == owner:
            id1 = dict1["id"]
            break

    headers = {
        'Authorization': 'Bearer '+access_token,
        'Content-type': 'application/json',
        'Accept': 'application/json',
    }
    num_co = random.randint(1000,9999)
    data = '{"correlation":"'+str(num_co)+'"}'
    link = 'https://'+tenant+'/v2.0/factors/emailotp/'+id1+'/verifications'
    response = requests.post(link, headers=headers, data=data)
    response_dict = json.loads(response.text)
    print(response_dict)
    txn_id = response_dict["id"]
    return txn_id,id1
    

def send_otp_to_mobile(number):
    headers = {
        'Authorization': 'Bearer '+access_token,
        'Content-type': 'application/json',
        'Accept': 'application/json',
    }
    num_co = random.randint(1000,9999)
    data = '{"correlation":"'+str(num_co)+'","phoneNumber": "'+number+'"}'
    link = 'https://'+tenant+'/v2.0/factors/smsotp/transient/verifications'
    response = requests.post(link, headers=headers, data=data)
    response_dict = json.loads(response.text)
    txn_id = response_dict["id"]
    print(f"\nSending OTP to {number}")
    return txn_id

def check_otp(otp,txn_id,enrollment_id=None):
    if enrollment_id is None:
        headers = {
        'Authorization': 'Bearer '+access_token,
        'Content-type': 'application/json',
        'Accept': 'application/json',
        }
        data = '{"otp": "'+otp+'"}'
        link = 'https://'+tenant+'/v2.0/factors/smsotp/transient/verifications/'+txn_id
        response = requests.post(link, headers=headers, data=data)
    else:
        headers = {
        'Authorization': 'Bearer '+access_token,
        'Content-type': 'application/json',
        'Accept': 'application/json',
        }
        data = '{"otp": "'+otp+'"}'
        link = 'https://'+tenant+'/v2.0/factors/emailotp/'+enrollment_id+'/verifications/'+txn_id
        response = requests.post(link, headers=headers, data=data)


    if response.status_code == 204:
        return True
    return False

                                 
def ui():
    flag = None
    layout = [  #[sg.Text(" "*30),sg.Image(r'C:\Users\VrushalChaudhari\Downloads\c79b1246-05b4-41f1-9104-b4fca0f6d18f_200x200.png')],
            [sg.Text('USERNAME '), sg.InputText(key="username")],
            [sg.Text()],
            [sg.Text('PASSWORD'), sg.InputText(password_char='*',key='password')],
            [sg.Text()],
            [sg.Text(" "*42),sg.Button('Submit') ]
    ]
    window1 = sg.Window(title="LOGIN", layout=layout, size=(1000, 500), margins = (200,50))

    while True:
        event, value = window1.read()
        if event in (sg.WIN_CLOSED,'Cancel',None):	# if user closes window or clicks cancel
            sys.exit()
        elif event == "Submit":
            username = value["username"]
            password = value["password"]
            print(username)
            print(password)
            if not(password == first_factor_password):
                window1.close()
                window1 = sg.Window(title="WRONG PASSWORD", layout=[[sg.Text('WRONG PASSWORD ENTERED')]], size=(1000,500),margins=(375, 200))
            else:
                email,number,owner = get_options(username)
                window1.close()
                layout_option = [[sg.Text(f'First Factor Authentication successful for {username}')],
                                 [sg.Text()],
                                 [sg.Text(f'User email  identified : {email}')],
                                 [sg.Text(f'User number identified : {number}')],
                                 [sg.Text()],
                                 [sg.Text("Select one of two choice for Second Factor Authentication")],
                                 [sg.Text()],
                                 [sg.Button('Send-OTP-to-email'),sg.Button('Send-OTP-to-mobile')]
                                ]
                window1 = sg.Window(title="CORRECT PASSWORD", layout=layout_option, size=(1000,500),margins=(300, 150))
        elif event == "Send-OTP-to-email":
            flag = "email"
            txn_id,enrollment_id = send_otp(email,owner)
            window1.close()
            layout_otp = [[sg.Text(f'Sending OTP to {email}')],
                          [sg.Text()],
                          [sg.Text('Enter OTP '), sg.InputText(key="co-relation",size=(20,1)),sg.Text(" - "),sg.InputText(key="otp",size=(20,1))],
                          [sg.Text()],
                          [sg.Button('Submit-OTP')]
                         ]
            window1 = sg.Window(title="OTP SUBMIT", layout=layout_otp, size=(1000,500),margins=(300, 150))
        elif event == "Send-OTP-to-mobile":
            flag = "mobile"
            txn_id = send_otp_to_mobile(number)
            window1.close()
            layout_otp = [[sg.Text(f'Sending OTP to {number}')],
                          [sg.Text()],
                          [sg.Text('Enter OTP '), sg.InputText(key="co-relation",size=(20,1)),sg.Text(" - "),sg.InputText(key="otp",size=(20,1))],
                          [sg.Text()],
                          [sg.Button('Submit-OTP')]
                         ]
            window1 = sg.Window(title="OTP SUBMIT", layout=layout_otp, size=(1000,500),margins=(300, 150))
        elif event == "Submit-OTP":
            otp = value["otp"]
            if flag == "email":
                con = check_otp(otp,txn_id,enrollment_id)
            elif flag == "mobile":
                con = check_otp(otp,txn_id)
            window1.close()
            if con:
                layout_pass = [[sg.Text('WELCOME TO TECH Solutions')]#,
                               #[sg.Image(r'C:\Users\VrushalChaudhari\Downloads\c79b1246-05b4-41f1-9104-b4fca0f6d18f_200x200.png')]
                              ]
                window1 = sg.Window(title="WELCOME", layout=layout_pass, size=(1000,500),margins=(300, 150))
            else:
                layout_fail = [[sg.Text('ENTERED OTP IS WRONG')]]
                window1 = sg.Window(title="REJECT", layout=layout_fail, size=(1000,500),margins=(375, 200))              



ui()

    
