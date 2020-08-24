# GUI for MFA using IBM Security Verify
Using curl/REST API's of IBM Security Verify GUI is made for multi factor authentication

Pre-requisite -  python >= 3.6

requirements -      
1)  python -m pip install PySimpleGUI
2)  python -m pip install requests

How to Run - 
1) edit secrets.json file with your client id , client secret and tenant name
2) python gui.py

currently first factor authenication is done using a single password and In second factor authentication API's are used.     
first_factor_password is Passw0rd .  you can change it in gui.py (change this line , first_factor_password = "Passw0rd").

# demo for email otp
![email otp demo](gif/gui-demo-email.gif)

# demo for sms otp
![sms otp demo](gif/gui-demo-sms.gif)



```Note: The project list easy step of implementation and is DO-IT-YOURSELF (DIY). It is avalaible ‘as is’ with no formal support from IBM. You are also welcome & encouraged to contribute to the project.```
