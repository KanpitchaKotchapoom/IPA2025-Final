#######################################################################################
# Yourname: Kanpitcha Kotchapoom
# Your student ID: 66070238
# Your GitHub Repo: https://github.com/KanpitchaKotchapoom/IPA2025-Final.git

#######################################################################################
# 1. Import libraries for API requests, JSON formatting, time, os, (restconf_final or netconf_final), netmiko_final, and ansible_final.

import requests
import json
import time
import os
import restconf_final
import netconf_final
import netmiko_final
import ansible_final
from requests_toolbelt.multipart.encoder import MultipartEncoder
from dotenv import load_dotenv

load_dotenv()

#######################################################################################
# 2. Assign the Webex access token to the variable ACCESS_TOKEN using environment variables.

ACCESS_TOKEN = os.environ["MY_ACCESS_TOKEN"]
MY_STUDENT_ID = os.environ["MY_STUDENT_ID"]

#######################################################################################
# 3. Prepare parameters get the latest message for messages API.

# Defines a variable that will hold the roomId
roomIdToGetMessages = (
    os.environ["WEBEX_ROOM_ID"]
)

ROUTER_IP = ["10.0.15.61", "10.0.15.62", "10.0.15.63", "10.0.15.64", "10.0.15.65"]
current_method = None

while True:
    # always add 1 second of delay to the loop to not go over a rate limit of API calls
    time.sleep(1)

    # the Webex Teams GET parameters
    #  "roomId" is the ID of the selected room
    #  "max": 1  limits to get only the very last message in the room
    getParameters = {"roomId": roomIdToGetMessages, "max": 1}

    # the Webex Teams HTTP header, including the Authoriztion
    getHTTPHeader = {"Authorization": "Bearer " + ACCESS_TOKEN}

# 4. Provide the URL to the Webex Teams messages API, and extract location from the received message.
    
    # Send a GET request to the Webex Teams messages API.
    # - Use the GetParameters to get only the latest message.
    # - Store the message in the "r" variable.
    r = requests.get(
        "https://webexapis.com/v1/messages",
        params=getParameters,
        headers=getHTTPHeader,
    )
    # verify if the retuned HTTP status code is 200/OK
    if not r.status_code == 200:
        raise Exception(
            "Incorrect reply from Webex Teams API. Status code: {}".format(r.status_code)
        )

    # get the JSON formatted returned data
    json_data = r.json()

    # check if there are any messages in the "items" array
    if len(json_data["items"]) == 0:
        raise Exception("There are no messages in the room.")

    # store the array of messages
    messages = json_data["items"]
    
    # store the text of the first message in the array
    message = messages[0]["text"]
    print("Received message: " + message)

    # check if the text of the message starts with the magic character "/" followed by your studentID and a space and followed by a command name
    #  e.g.  "/66070123 create"
    if message.startswith(f"/{MY_STUDENT_ID}"):

        # extract the command
        parts = message.split()
        len_parts = len(parts)
        action_command = None
        ip = None
        responseMessage = "Error: Unprocessed command"

        part1_commands = ["create", "delete", "enable", "disable", "status"]
        netmiko_commands = ["gigabit_status"]
        ansible_commands = ["showrun"]

# 5. Complete the logic for each command
        if len_parts < 2:
            responseMessage = "Error: No command provided."
        else:
            arg1 = parts[1]

            if len_parts == 2:
                if arg1 == "restconf":
                    current_method = "restconf"
                    responseMessage = "Ok: Restconf"
                elif arg1 == "netconf":
                    current_method = "netconf"
                    responseMessage = "Ok: Netconf"

                elif arg1 in part1_commands:
                    if current_method is None:
                        responseMessage = "Error: No method specified"
                    else:
                        responseMessage = "Error: No IP specified"

                elif arg1 in ROUTER_IP:
                    responseMessage = "Error: No command found."

                else:
                    responseMessage = f"Error: Unknown command or invalid format: {arg1}"
            elif len_parts == 3:
                arg2 = parts[2]

                if arg1 in netmiko_commands:
                    ip = arg2
                    if ip not in ROUTER_IP:
                        responseMessage = f"Error: Invalid IP: {ip}"
                    else:
                        action_command = arg1
                        responseMessage = netmiko_final.gigabit_status(ip)
                
                elif arg1 in ansible_commands:
                    ip = arg2
                    if ip not in ROUTER_IP:
                        responseMessage = f"Error: Invalid IP: {ip}"
                    else:
                        action_command = arg1
                        responseMessage = ansible_final.showrun(ip, MY_STUDENT_ID)

                elif arg1 in ROUTER_IP and arg2 == "motd":
                    ip = arg1
                    action_command = "get_motd"
                    responseMessage = netmiko_final.get_motd(ip)

                elif arg1 in ROUTER_IP:
                    ip = arg1
                    action_command = arg2

                    if action_command not in part1_commands:
                        if action_command in netmiko_commands:
                            responseMessage = netmiko_final.gigabit_status(ip)
                        elif action_command in ansible_commands:
                            responseMessage = ansible_final.showrun(ip, MY_STUDENT_ID)
                        else:
                            responseMessage = f"Error: Unknown command: {action_command}"
                    
                    elif current_method is None:
                        responseMessage = "Error: No method specified"

                    elif current_method == "restconf":
                        if action_command == "create": responseMessage = restconf_final.create(MY_STUDENT_ID, ip)
                        elif action_command == "delete": responseMessage = restconf_final.delete(MY_STUDENT_ID, ip)
                        elif action_command == "enable": responseMessage = restconf_final.enable(MY_STUDENT_ID, ip)
                        elif action_command == "disable": responseMessage = restconf_final.disable(MY_STUDENT_ID, ip)
                        elif action_command == "status": responseMessage = restconf_final.status(MY_STUDENT_ID, ip)
                    
                    elif current_method == "netconf":
                        if action_command == "create": responseMessage = netconf_final.create(MY_STUDENT_ID, ip)
                        elif action_command == "delete": responseMessage = netconf_final.delete(MY_STUDENT_ID, ip)
                        elif action_command == "enable": responseMessage = netconf_final.enable(MY_STUDENT_ID, ip)
                        elif action_command == "disable": responseMessage = netconf_final.disable(MY_STUDENT_ID, ip)
                        elif action_command == "status": responseMessage = netconf_final.status(MY_STUDENT_ID, ip)

                else:
                    responseMessage = "Error: Invalid command format."
            elif len_parts >= 4 and parts[1] in ROUTER_IP and parts[2] == "motd":
                ip = parts[1]
                action_command = "set_motd"

                motd_message = " ".join(parts[3:])

                if ip not in ROUTER_IP:
                    responseMessage = f"Error: Invalid IP: {ip}"
                else:
                    print(motd_message)
                    responseMessage = ansible_final.set_motd(ip, motd_message)
            else:
                responseMessage = "Error: Invalid command format. Too many arguments."

# 6. Complete the code to post the message to the Webex Teams room.

        # The Webex Teams POST JSON data for command showrun
        # - "roomId" is is ID of the selected room
        # - "text": is always "show running config"
        # - "files": is a tuple of filename, fileobject, and filetype.

        # the Webex Teams HTTP headers, including the Authoriztion and Content-Type
        
        # Prepare postData and HTTPHeaders for command showrun
        # Need to attach file if responseMessage is 'ok'; 
        # Read Send a Message with Attachments Local File Attachments
        # https://developer.webex.com/docs/basics for more detail

        if action_command == "showrun" and responseMessage == "ok":
            filename = f'show_run_{MY_STUDENT_ID}_{ip}.txt'
            fileobject = open(filename, "rb")
            filetype = "text/plain"
            postData = {
                "roomId": roomIdToGetMessages,
                "text": "show running config",
                "files": (filename, fileobject, filetype),
            }
            postData = MultipartEncoder(fields=postData)
            HTTPHeaders = {
                "Authorization": "Bearer " + ACCESS_TOKEN,
                "Content-Type": postData.content_type,
            }
        # other commands only send text, or no attached file.
        else:
            postData = {"roomId": roomIdToGetMessages, "text": responseMessage}
            postData = json.dumps(postData)

            # the Webex Teams HTTP headers, including the Authoriztion and Content-Type
            HTTPHeaders = {"Authorization": "Bearer " + ACCESS_TOKEN, "Content-Type": "application/json"}   

        # Post the call to the Webex Teams message API.
        r = requests.post(
            "https://webexapis.com/v1/messages",
            data=postData,
            headers=HTTPHeaders,
        )

        if action_command == "showrun" and responseMessage == "ok":
            fileobject.close()

        if not r.status_code == 200:
            raise Exception(
                "Incorrect reply from Webex Teams API. Status code: {}".format(r.status_code)
            )