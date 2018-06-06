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

from modelClass import DnacClientClass
from modelClass import DnacSiteHierarchyClass
from modelClass import DnacNetworkDeviceDetailClass
from modelClass import DnacNetworkDeviceClass

def getClientDetail(timestamp,macAddr,apiObj):
    clientDetail=None;
    if apiObj is not None:

        path = "/dna/intent/api/v1/client-detail?"
        query = "?timestamp="+str(timestamp)+"&macAddress="+macAddr
        headers = {'__runsync': 'true'}

        #todo Change to GET after hotfix is released
        clientJson = apiObj.get(path+query, headers);

        if 'response' in clientJson:
            response = clientJson['response']
            if 'detail' in response:
                clientDetailObj = response['detail']
                for health in clientDetailObj['healthScore']:
                    if(health['healthType']=='OVERALL'):
                        overallHealthScore= health['score']
                clientDetail= DnacClientClass(overallHealthScore,clientDetailObj['hostName'],clientDetailObj['hostMac'],clientDetailObj['hostIpV4'],clientDetailObj['clientConnection'],clientDetailObj['connectionStatus'])

    return clientDetail;

def getSiteHierarchy(timestamp,apiObj):
    #timestamp=1527103419000&searchBy=Starbucks-AP1&identifier=nwDeviceName

    path = "/dna/intent/api/v1/site-hierarchy?"
    query = "timestamp="+str(timestamp)
    headers = {'__runsync': 'true'}
    siteObjJson = apiObj.get(path+query, headers);

    if siteObjJson is not None:
        if 'response' in siteObjJson :
            resp = siteObjJson['response']
            siteList=[]

            for row in resp:
                print(row)
                site = DnacSiteHierarchyClass(row['siteName'],row['siteId'],row['parentSiteId'],row['healthyNetworkDevicePercentage'],
                                              row['healthyClientsPercentage'],row['numberOfNetworkDevice'],row['overallGoodDevices'])
                siteList.append(site)
            return siteList
    return None

def getNetworkDevice(timestamp,searchBy,identifier,apiObj):
    if apiObj is not None:

        #timestamp=1527103419000&searchBy=Starbucks-AP1&identifier=nwDeviceName
        path = "/dna/intent/api/v1/network-device-detail?"
        query = "timestamp="+str(timestamp)+"&searchBy="+searchBy+"&identifier="+identifier
        headers = {'__runsync': 'true'}
        networkDevJson = apiObj.get(path+query, headers);

        if networkDevJson is not None:
            if 'response' in networkDevJson:
                resp = networkDevJson['response']
                networkDevDetail = DnacNetworkDeviceClass(resp['nwDeviceName'],resp['serialNumber'],resp['managementIpAddr'],resp['opState'],
                                                          resp['platformId'], resp['nwDeviceId'], resp['sysUptime'],
                                                          resp['mode'],resp['resetReason'],resp['nwDeviceRole'],resp['upTime'],resp['nwDeviceFamily'],
                                                          resp['macAddress'], resp['connectedTime'], resp['softwareVersion'],
                                                          resp['subMode'],resp['nwDeviceType'], resp['overallHealth'], resp['memoryScore'],resp['cpuScore'])


                return networkDevDetail
    return None


def getAllNetworkDevices(apiObj):

    devicesList=[];

    devices_path = "/api/v1/network-device"
    deviceObj = apiObj.get(devices_path)

    for response in deviceObj["response"]:
        deviceObject=DnacNetworkDeviceDetailClass(response['hostname'],response['instanceUuid'],response['family'],response['type'],response['macAddress'],response['serialNumber'])
        devicesList.append(deviceObject)

    return devicesList



