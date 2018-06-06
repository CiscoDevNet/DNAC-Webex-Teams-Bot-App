"""
Copyright (c) 2018 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.0 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

"""
This file contains code to process the incoming messages from WebEx-Teams and to send messages back

"""
import jinja2
import imgkit
from flask import Flask, render_template
import requests
from flask import request
import sys
import matplotlib.pyplot as plt
import numpy as np

import api
import dnacapi
import json
import time
from requests_toolbelt.multipart.encoder import MultipartEncoder


app = Flask(__name__, static_folder='../static/dist', template_folder='../static')

'''
Set the bearer token, email ,name etc
'''
bearer = "YjExNjIzOTctNDNhNy00NTQ2LThhYTctOGQ0ZjEyNGVhMjFhNGQ2ZTQ4NzAtOGFj"
bot_email = 'bot-a-dna@sparkbot.io'
bot_name = "bot-a-dna"
line_separator = "\n******************************************************************************************\n"

#Global API Object
apiObj = None

"""
******************  SPARK API - GET , POST , POST IMAGE ****************************
"""


def sendSparkGET(url):
    """
    Method to read messages from the WebEx-Teams(Spark) Room
    :param url:
    :return:
    """

    headers = {"Accept": "application/json",
               "Content-Type": "application/json",
               "Authorization": "Bearer " + bearer}

    message_from_spark = requests.get(url, verify=False,
                               headers=headers, stream=True)

    return message_from_spark


def sendSparkPOST(url, data):
    """
    This method is used for:
        -posting a message to the WebEx-Teams(Spark) room to confirm that a command was received and processed
    """
    headers = {"Accept": "application/json",
               "Content-Type": "application/json",
               "Authorization": "Bearer " + bearer}

    contents = requests.post(url, json.dumps(data),
                             headers=headers)
    return contents


def postImageToSpark(webhook,imageName,description):

    """
    Method to post an image to the WebEx-Teams(Spark) room
    :param webhook:
    :param imageName:
    :param description:
    :return:
    """
    media = MultipartEncoder({'roomId': webhook['data']['roomId'],
                          'text': 'Image attached',
                          'files': (description, open(imageName, 'rb'),
                                    'image/jpg')})

    requests.post('https://api.ciscospark.com/v1/messages', data=media,
                      headers={'Authorization': 'Bearer ' + bearer,
                               'Content-Type': media.content_type})


""" 
************************************  End Spark APIs ************************************
"""

@app.route('/', methods=['POST'])
def index():
    """
    When messages come in from the webhook, they are processed here.  The message text needs to be retrieved from Spark,
    using the sendSparkGet() function.  The message text is parsed.  If an expected command is found in the message,
    further actions are taken.
    """

    webhook = json.loads(request.data.decode("utf-8"))
    result = sendSparkGET('https://api.ciscospark.com/v1/messages/{0}'.format(webhook['data']['id']))
    result = json.loads(result.text)

    # If the message is not from the BOT - process the message
    if webhook['data']['personEmail'] != bot_email:
        in_message = result.get('text', '')
        processMessage(in_message, webhook)

    return "true"




def processMessage(in_message, webhook):
    """
    Handle the different types of messages
    :param in_message:
    :param webhook:
    :return:
    """
    # Handle greeting
    if 'hello' in in_message.lower() or "whoareyou" in in_message.lower() or "hi" in in_message.lower():
        handleGreeting(in_message, webhook)

    # Connect to a cluster
    elif 'connect' in in_message.lower():
        handleConnection(in_message, webhook)

    # site Health Summary
    elif 'list-devices' in in_message:
        handleListDevices(webhook)

    # Handle Client detail
    elif 'client' in in_message:
        handleClient(in_message, webhook)

    #Handle Device detail
    elif 'device' in in_message:
        handleNetworkDevice(in_message, webhook)

    # Site Health Detail
    elif 'site-health-detail' in in_message:
        handleSiteHierarchy(webhook,True)

    #site Health Summary
    elif 'site-health-summary' in in_message:
        handleSiteHierarchy(webhook,False)

    # Help
    elif 'help' in in_message:
        handleHelp(webhook)

    #logout
    elif 'logout' in in_message.lower():
        handleLogout(webhook)

    #show help if unable to understand the message
    else:
        handleHelp(webhook)


def handleGreeting(in_message, webhook):
    """
    Method to handle the greeting when the client types a hi or hello
    :param in_message:
    :param webhook:
    :return:
    """
    greeting = line_separator + "\tHello! I'm your bot-a-dna!\t" + u"\U0001F44B" + line_separator
    connect="Key in your IP ,Username & Password to connect. Example: **Connect,10.0.0.0,admin,Password123**"

    sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": greeting})
    sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "markdown": connect})

def handleConnection(in_message, webhook):
    """
    Method to connect to the cluster using credentials provided and save the token until
    user decided to end session
    :param in_message:
    :param webhook:
    :return:
    """
    cmd, ipAddr, username, password = in_message.split(",")
    global apiObj
    apiObj = api.Api(ip=ipAddr, username=username, password=password)
    if apiObj is not None:
        msg = "**Connected Successfully!**\t\t"+ u"\u2713"
        sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "markdown": msg})
        msg =       "Please try the commands to chat with me"+ line_separator
        msg = msg + "1. connect,<IP>,<UI-Username>,<UI-Password>       Connect to a cluster\n"
        msg = msg + "2. client <MAC ADDRESS>                                              Current information about a client\n"
        msg = msg + "3. device <DEVICE NAME>                                              Current information about a network device\n"
        msg = msg + "4. site-health-summary                                                   Healthy Unhealthy devices in a network\n"
        msg = msg + "5. site-health-detail                                                          Detailed health information per Site\n"
        msg = msg + "6. list-devices                                                                     Lists Devices on the network\n"
        msg = msg + "7. help                                                                                 Detailed health information per Site\n"
        msg = msg + "8. logout                                                                              Disconnect current connection to cluster\n"
    else:
        msg = "Cluster credentials incorrect/ Unable to authenticate.Please try again"
    sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": msg})


def validateConnection():
    if apiObj is not None:
        return True
    else:
        return False


def handleClient(in_message, webhook):
    """
    Method to get the client detail based on a MAC Address
    :param in_message:
    :param webhook:
    :return:
    """
    if validateConnection():

        cmd, clientmac = in_message.split(" ")

        # Send a wait message
        waitMessage = 'Please wait while I fetch the data   ' + u"\U0001F557"
        sendSparkPOST("https://api.ciscospark.com/v1/messages",
                      {"roomId": webhook['data']['roomId'], "text": str(waitMessage)})

        # get client details for MAC from API
        millis = int(round(time.time() * 1000))
        clientData = dnacapi.getClientDetail(str(millis),clientmac,apiObj)

        # Create an image with the text from output- Jinja
        if clientData is not None:
            context = {
                'hostName': clientData.hostName,
                'status': clientData.status,
                'healthScore': clientData.healthscore,
                'macAddress': clientData.macAddress,
                'ip': clientData.ipv4,
                'connection': clientData.connection

            }

            result = jinja2.Environment(
                loader=jinja2.FileSystemLoader('./templates/')
            ).get_template('client_detail.html').render(context)

            f = open("templates/client_detail_gen.html", 'w')
            f.write(result)
            f.close()
            fileName = 'client_detail.jpg'
            imgkit.from_file('templates/client_detail_gen.html', fileName)

            postImageToSpark(webhook, fileName, 'Client Detail:' + clientmac)
        else:
            data = 'I cannot find this client on the network.Can you try a different MAC?'
            sendSparkPOST("https://api.ciscospark.com/v1/messages",
                          {"roomId": webhook['data']['roomId'], "text": data})
    else:
        msg = "Not connected to any cluster, please connect and try again."
        sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": msg})


def handleNetworkDevice(in_message, webhook):
    """
    Method to get the Network Device Detail
    :param in_message:
    :param webhook:
    :return:
    """

    if validateConnection():
        cmd, deviceName = in_message.split(" ")

        # Send a wait message
        waitMessage = 'Please wait while I fetch the data   '+ u"\U0001F557"
        sendSparkPOST("https://api.ciscospark.com/v1/messages",
                      {"roomId": webhook['data']['roomId'], "text": str(waitMessage)})

        timestamp = int(round(time.time() * 1000))
        networkDevice = dnacapi.getNetworkDevice(timestamp,deviceName,'nwDeviceName',apiObj)

        if networkDevice is not None:
            context = {
                'nwDeviceName': networkDevice.name,
                'macAddress': networkDevice.macAddress,
                'ip': networkDevice.name,
                'upTime': networkDevice.upTime,
                'platformId': networkDevice.platformId,
                'overallHealth': networkDevice.overallHealth,
                'memoryScore': networkDevice.memoryScore,
                'cpuScore': networkDevice.cpuScore

            }

            result = jinja2.Environment(
                loader=jinja2.FileSystemLoader('./templates/')
            ).get_template('network_device.html').render(context)

            f = open("templates/network_device_gen.html", 'w')
            f.write(result)
            f.close()
            fileName='network_dev.jpg'
            imgkit.from_file('templates/network_device_gen.html', fileName)

            postImageToSpark(webhook,fileName,'Network Device:'+deviceName)
        else:
            data = 'I cannot find this device on the network.Can you try a different device name?'
            sendSparkPOST("https://api.ciscospark.com/v1/messages",
                          {"roomId": webhook['data']['roomId'], "text": data})
    else:
        msg = "Not connected to any cluster, please connect and try again."
        sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": msg})


def handleSiteHierarchy(webhook,detail):
    if validateConnection():
        waitMessage = 'Please wait while I fetch the data   ' + u"\U0001F557"
        sendSparkPOST("https://api.ciscospark.com/v1/messages",
                      {"roomId": webhook['data']['roomId'], "text": str(waitMessage)})

        #reducing time by 15 minutes for client health to show up
        timestamp = int(round(time.time() * 1000)-(15*60*1000))
        siteHierarchy = dnacapi.getSiteHierarchy(timestamp,apiObj)

        if siteHierarchy is not None:
            data= "Here is the Site Health for all your sites:"+ line_separator
            for site in siteHierarchy:
                if detail is True:
                    data = data + "Site Name: "+ site.name +"\n"
                    data = data + "Network Health: " + str(site.networkHealth) + "\n"
                    data = data + "Client Health: " + str(site.clienthealth) + "\n"
                    data = data + "Healthy Device Count: " + str(site.healthyDevCount) + "\n"
                    data = data + "Total Device Count: " + str(site.totalDevCount) + "\n\n"

                if detail is False:
                    if 'All Sites' in site.name:
                        filename='devicehealth.png'
                        drawDonut(site.healthyDevCount,(site.totalDevCount-site.healthyDevCount),filename)
                        postImageToSpark(webhook, filename, 'Overall Device Health for all Sites')

                        drawBarChart(site.networkHealth, site.clienthealth, filename)
                        postImageToSpark(webhook, filename, 'Overall Device Health for all Sites')

            if detail is True:
                sendSparkPOST("https://api.ciscospark.com/v1/messages",
                                  {"roomId": webhook['data']['roomId'], "text": data})

        else:
            data = 'Sorry! I am having some trouble now.Can you try again or try a different command?'
            sendSparkPOST("https://api.ciscospark.com/v1/messages",
                          {"roomId": webhook['data']['roomId'], "text": data})
    else:
        msg = "Not connected to any cluster, please connect and try again."
        sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": msg})


def handleListDevices(webhook):
    if validateConnection():
        waitMessage = 'Please wait while I fetch the data   ' + u"\U0001F557"
        sendSparkPOST("https://api.ciscospark.com/v1/messages",
                      {"roomId": webhook['data']['roomId'], "text": str(waitMessage)})

        deviceList = dnacapi.getAllNetworkDevices(apiObj)

        if deviceList is not None:
            data= "Here is the list of devices on your network:"+ line_separator
            for device in deviceList:
                data = data + "Name: "+ device.name+"\n"
                data = data + "MAC Address: " + device.macAddress.upper() + "\n\n"

            sendSparkPOST("https://api.ciscospark.com/v1/messages",
                                  {"roomId": webhook['data']['roomId'], "text": data})

        else:
            data = 'Sorry! I am having some trouble now.Can you try again or try a different command?'
            sendSparkPOST("https://api.ciscospark.com/v1/messages",
                          {"roomId": webhook['data']['roomId'], "text": data})
    else:
        msg = "Not connected to any cluster, please connect and try again."
        sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": msg})


def handleHelp(webhook):

    msg = "Please try the commands to chat with me" + line_separator
    msg = msg + "1. connect,<IP>,<UI-Username>,<UI-Password>       Connect to a cluster\n"
    msg = msg + "2. client <MAC ADDRESS>                                              Current information about a client\n"
    msg = msg + "3. device <DEVICE NAME>                                              Current information about a network device\n"
    msg = msg + "4. site-health-summary                                                   Healthy Unhealthy devices in a network\n"
    msg = msg + "5. site-health-detail                                                          Detailed health information per Site\n"
    msg = msg + "6. list-devices                                                                     Lists Devices on the network\n"
    msg = msg + "7. help                                                                                 Detailed health information per Site\n"
    msg = msg + "8. logout                                                                              Disconnect current connection to cluster\n"

    sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": msg})


def handleLogout(webhook):
    global apiObj
    apiObj = None
    msg = "**Good Bye**! "+	u"\U0001F44B" + "    Please connect again to check your system"
    sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "markdown": msg})


def drawDonut(healthy,unhealthy,filename):
    labels = 'Healthy Device(s):'+str(healthy), 'Unhealthy Device(s):'+str(unhealthy)
    sizes = [healthy,unhealthy]
    colors = ['green', 'orange']
    explode = (0, 0)  # explode a slice if required

    plt.pie(sizes, explode=explode, labels=labels, colors=colors, shadow=True)

    # draw a circle at the center of pie to make it look like a donut
    centre_circle = plt.Circle((0, 0), 0.75, color='black', fc='white', linewidth=1.25)
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)

    # Set aspect ratio to be equal so that pie is drawn as a circle.
    plt.axis('equal')
    plt.title('Overall Device Health')
    plt.savefig(filename)


def drawBarChart(networkHealth,clientHealth,filename):
    # Fixing random state for reproducibility
    np.random.seed(19680801)

    plt.rcdefaults()
    fig, ax = plt.subplots(figsize=(10, 6))

    # Example data
    people = ('Network', 'Client')
    y_pos = np.arange(len(people))
    # networkHealth = 20
    # clientHealth = 95

    if networkHealth > 60:
        networkColor = 'green'
    elif networkHealth > 30:
        networkColor = 'goldenrod'
    else:
        networkColor = 'red'

    if clientHealth > 60:
        clientColor = 'green'
    elif clientHealth > 30:
        clientColor = 'goldenrod'
    else:
        clientColor = 'red'

    performance = (networkHealth, clientHealth)
    error = np.random.rand(len(people))

    ax.barh(y_pos, performance, xerr=error, align='center',
            color=(networkColor, clientColor), ecolor='black', height=0.2)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(people)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel('Health(%)')
    ax.set_title('Overall Site Health')

    plt.savefig(filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10010, debug=True)


