# -*- coding: utf-8 -*-
import datetime
import random
import time
import os
import requests
import smtplib
from configparser import ConfigParser
from email.mime.text import MIMEText
import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.vpc.v20170312 import vpc_client, models

config = ConfigParser()
configPath = os.path.dirname(os.path.abspath(__file__))
config.read(os.path.join(configPath, 'config.ini'), encoding='UTF-8')
senderMail = config.get('mail', 'senderMail')  # 发送者邮箱地址
authCode = config.get('mail', 'authCode')  # 发送者 QQ邮箱授权码
receiverMail = config.get('mail', 'receiverMail')  # 接收者邮箱地址
ak = config.get('cloud', 'ak')  # 腾讯云 ak
sk = config.get('cloud', 'sk')  # 腾讯云 sk
instanceId = config.get('cloud', 'instanceId')  # 腾讯云云主机 ID，已指定


# 发送邮件
def send_mail(subject, content):
    """
    :param content: 邮件内容
    :return: 发送状态
    """
    subject = subject  # 邮件主题
    content = content  # 邮件内容
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = senderMail
    msg['To'] = receiverMail
    try:
        server = smtplib.SMTP_SSL('smtp.qq.com', smtplib.SMTP_SSL_PORT)
        server.login(senderMail, authCode)
        server.sendmail(senderMail, receiverMail, msg.as_string())
        print('邮件发送成功')
    except smtplib.SMTPException as e:
        print('邮件发送异常', e)
    finally:
        quit()


# 查看绑定实例的腾讯云弹性 IP
def find_bund_tencent_cloud_ip():
    time_stamp = datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S')
    try:
        cred = credential.Credential(ak, sk)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "vpc.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = vpc_client.VpcClient(cred, "ap-shanghai", clientProfile)

        req = models.DescribeAddressesRequest()
        params = {"Filters": [{"Values": [instanceId], "Name": "instance-id"}]}
        req.from_json_string(json.dumps(params))
        resp = client.DescribeAddresses(req).to_json_string()
        Response = resp.get('Response')
        AddressSet = Response.get('AddressSet')[0]
        AddressId = AddressSet.get('AddressId')  # 绑定实例的 eip id
        content = time_stamp + "查看绑定实例的腾讯云弹性 IP 成功"
        print(content)
        return AddressId

    except TencentCloudSDKException as err:
        content = time_stamp + "异常：查看绑定实例的腾讯云弹性 IP " + err
        print(content)


# 解绑腾讯云弹性 IP
def unbund_tencent_cloud_ip():
    time_stamp = datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S')
    try:
        cred = credential.Credential("AKIDofJm86Jf7JcgXCm280g9NQErLelerwIP",
                                     "eBV0pQ4TdbNuNdhcMr7ORVW2KSLVZOyP")
        httpProfile = HttpProfile()
        httpProfile.endpoint = "vpc.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = vpc_client.VpcClient(cred, "ap-shanghai", clientProfile)
        req = models.DisassociateAddressRequest()
        AddressId = find_bund_tencent_cloud_ip()
        params = {"AddressId": AddressId}
        req.from_json_string(json.dumps(params))
        resp = client.DisassociateAddress(req).to_json_string()
        subject = '解绑弹性 IP 成功'
        content = time_stamp + "成功：解绑弹性 IP " + resp
        send_mail(subject, content)
        print(content)
    except TencentCloudSDKException as err:
        subject = '警告：解绑弹性 IP失败'
        content = time_stamp + "解绑弹性 IP失败 " + err
        send_mail(subject, content)
        print(content)


# 释放腾讯云弹性 IP
def release_tencent_cloud_ip():
    time_stamp = datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S')
    try:
        cred = credential.Credential(ak, sk)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "vpc.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = vpc_client.VpcClient(cred, "ap-shanghai", clientProfile)

        req = models.ReleaseAddressesRequest()
        AddressId = find_bund_tencent_cloud_ip()
        params = {"AddressIds": [AddressId]}
        req.from_json_string(json.dumps(params))
        resp = client.ReleaseAddresses(req).to_json_string()
        subject = '释放弹性 IP 成功'
        content = time_stamp + "成功释放弹性 IP " + resp
        send_mail(subject, content)
        print(content)

    except TencentCloudSDKException as err:
        subject = '警告：释放弹性 IP 失败'
        content = time_stamp + "释放弹性 IP失败 " + err
        send_mail(subject, content)
        print(content)


# 申请腾讯云弹性 IP
def creat_tencent_cloud_ip():
    time_stamp = datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S')
    try:
        cred = credential.Credential(ak, sk)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "vpc.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = vpc_client.VpcClient(cred, "ap-shanghai", clientProfile)

        req = models.AllocateAddressesRequest()
        params = {}
        req.from_json_string(json.dumps(params))

        resp = client.AllocateAddresses(req).to_json_string()
        Response = resp.get('Response')
        AddressSet = resp.get('AddressSet')[0]
        AddressId = resp.get('AddressSet')[0]
        subject = '新建弹性 IP 成功'
        content = time_stamp + "成功新建弹性 IP " + resp
        send_mail(subject, content)
        print(content)
        return AddressId

    except TencentCloudSDKException as err:
        subject = '警告：新建弹性 IP 失败'
        content = time_stamp + "新建弹性 IP失败 " + err
        send_mail(subject, content)
        print(content)


# 绑定腾讯云弹性 IP
def bund_tencent_cloud_ip():
    time_stamp = datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S')
    try:
        cred = credential.Credential(ak, sk)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "vpc.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = vpc_client.VpcClient(cred, "ap-shanghai", clientProfile)

        req = models.AssociateAddressRequest()
        AddressId = creat_tencent_cloud_ip()
        params = {"AddressId": AddressId, "InstanceId": instanceId}
        req.from_json_string(json.dumps(params))
        resp = client.AssociateAddress(req).to_json_string()
        subject = '新建弹性 IP 成功'
        content = time_stamp + "成功新建弹性 IP " + resp
        send_mail(subject, content)
        print(content)

    except TencentCloudSDKException as err:
        subject = '警告：绑定弹性 IP 失败'
        content = time_stamp + "绑定弹性 IP失败 " + err
        send_mail(subject, content)
        print(content)


# 解析航班信息
def parse_flight(flightInfoList, time_stamp):
    for flightInfo in flightInfoList:
        for cabinFare in flightInfo['cabinFareList']:
            if cabinFare['cabinCode'] == 'X':
                # for airName in airNames:
                carrierNoName = flightInfo.get('carrierNoName')
                # if carrierNoName == airName:
                arrCityName = flightInfo.get('arrCityName')
                arrAirportName = flightInfo.get('arrAirportName')
                arrTerm = flightInfo.get('arrTerm')
                flightDate = flightInfo.get('flightDate')  # 航班日期
                arrDateTime = flightInfo.get('arrDateTime')[-5:]
                depCityName = flightInfo.get('depCityName')
                depAirportName = flightInfo.get('depAirportName')
                depTerm = flightInfo.get('depTerm')
                depDateTime = flightInfo.get('depDateTime')[-5:]
                cabinNumber = cabinFare['cabinNumber']
                content = '航班:{}, 日期: {}, 出发地: {}, 到达地: {}, 时间: {}~{}  '.format(
                    carrierNoName, flightDate,
                    depCityName + depAirportName + depTerm,
                    arrCityName + arrAirportName + arrTerm, depDateTime,
                    arrDateTime)
                # if cabinNumber == 'A' and carrierNoName in {'吉祥HO1107': '厦门',  '吉祥HO1105': '厦门',  '吉祥HO1198': '厦门',  '吉祥HO1108': '厦门'}:
                if cabinNumber == 'A' and carrierNoName in {
                        '吉祥HO1074': '武汉',
                        '吉祥HO1177': '三亚',
                        '吉祥HO1207': '贵阳',
                        '吉祥HO1142': '贵阳',
                        '吉祥HO1248': '重庆',
                        '吉祥HO1243': '重庆',
                        '吉祥HO1267': '重庆',
                }:
                    subject = '{}-{}：监控航班出现余票'.format(
                        depCityName + depAirportName + depTerm,
                        arrCityName + arrAirportName + arrTerm)
                    content = content + '该航班可以兑换畅飞卡座位！'
                    send_mail(subject, content)
                elif (cabinNumber == 'A'
                      or int(cabinNumber) > 0) and carrierNoName in {
                          '吉祥HO1074': '武汉',
                          '吉祥HO1177': '三亚',
                          '吉祥HO1207': '贵阳',
                          '吉祥HO1142': '贵阳',
                          '吉祥HO1248': '重庆',
                          '吉祥HO1243': '重庆',
                          '吉祥HO1267': '重庆',
                      }:
                    subject = '{}-{}：监控航班出现余票'.format(
                        depCityName + depAirportName + depTerm,
                        arrCityName + arrAirportName + arrTerm)
                    content = content + '该航班剩余 %s 张畅飞卡座位！' % cabinNumber
                    send_mail(subject, content)
                else:
                    subject = '{}-{}：监控航班出现余票'.format(
                        depCityName + depAirportName + depTerm,
                        arrCityName + arrAirportName + arrTerm)
                    content = time_stamp + '  ' + content + '余座: %s' % cabinNumber
                    print(content)


# 请求航班接口
def requests_info(data):
    """
    :param data: 监控航班，data 需要在吉祥 m 站抓包拿到
    :return:
    """
    time_stamp = datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S')
    headers = {
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'versionCode': '17200',
        'User-Agent':
        'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
        'platformInfo': 'MWEB',
        'Content-Type': 'application/json;charset=UTF-8',
        'Accept': 'application/json, text/plain, */*',
        'channelCode': 'MWEB',
        'timeStamp': '1601259465395',
        'token': '',
        'clientVersion': '1.7.2',
        'Origin': 'https://m.juneyaoair.com',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://m.juneyaoair.com/flights/index.html',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    try:
        response = requests.post(
            'https://m.juneyaoair.com/server/v2/flight/AvFare',
            headers=headers,
            data=data.encode('utf-8')).json()
        # print(response)
        errorInfo = response.get("errorInfo")
        if errorInfo != '成功':
            release_tencent_cloud_ip()
            bund_tencent_cloud_ip()
            print(time_stamp, errorInfo)
            print(time_stamp, '自动替换 IP')
            exit()
        else:
            flightInfoList = response.get("flightInfoList")
            parse_flight(flightInfoList, time_stamp)
    except requests.exceptions.Timeout as e:
        print('请求超时：' + e)
    except requests.exceptions.HTTPError as e:
        print('http请求错误:' + e)


if __name__ == '__main__':
    blackBox = [
        'eyJ2IjoiNGhYNnhwMGNMOXc5KzVnRnkwNDErMDVYTTNQblgrOEZHMDhXTzZ2UXJEcVQrTUJxUHhaMUFWSXF5UFgyVlQzNCIsIm9zIjoid2ViIiwiaXQiOjE1NTQsInQiOiJaRERRekhwbzR5ODZ5Uk9Ec1BYYS8wOFl5ekF2elN1TVFTbEJxU0JmajNpTFB1ODF2aVd0bkZEUzZmNWp3czN0czd0dXRpQzJFWitISzloMWlFbXBBZz09In0=',
        'eyJ2IjoiZ3YrYXhwV0tWTkFhWCtmcDUyMjdiYTkxRGw0OXVPRmRYT0lCWWxMVUlnSzhnRHRZN3QrcENMOGplZDZLTEZBaCIsIm9zIjoid2ViIiwiaXQiOjIwOTIsInQiOiJCdjdrQmp0Z2thZGw5WkxSbzdERk5wVnZlNURVT3ZuNFRtaUtrdS9VT1dIRnJ6czJmYXo3bEFmYkJLc2ZQYjZBbnJoTExEdWk4NERtMVZWNTFHazEwZz09In0=',
        'eyJ2IjoiNGhYNnhwMGNMOXc5KzVnRnkwNDErMDVYTTNQblgrOEZHMDhXTzZ2UXJEcVQrTUJxUHhaMUFWSXF5UFgyVlQzNCIsIm9zIjoid2ViIiwiaXQiOjMxOSwidCI6InlVRWN3cHFTVi9PNmU5UkpsQmxoclRoZm1wMlplb25ZL3JZM2xZSVlVMithL0hwbkZpempXT0ZxQTJWLzFaTk56eXVzUjR6QjFNYlh0a3czZUFFQUh3PT0ifQ==',
        'eyJ2IjoiNGhYNnhwMGNMOXc5KzVnRnkwNDErMDVYTTNQblgrOEZHMDhXTzZ2UXJEcVQrTUJxUHhaMUFWSXF5UFgyVlQzNCIsIm9zIjoid2ViIiwiaXQiOjgzOCwidCI6IkFrREd5WUdvN3JWNm9ROVhYK1o0cWtxeXN4U29zU1E5bVRZRTVLMmhLNklIZTdsdVJ6RlN1Rkh4S1lzVks1ZmtTMGM1ZEZUbDRUNXZkbU41eUJQa0R3PT0ifQ==',
        'eyJ2IjoiNGhYNnhwMGNMOXc5KzVnRnkwNDErMDVYTTNQblgrOEZHMDhXTzZ2UXJEcVQrTUJxUHhaMUFWSXF5UFgyVlQzNCIsIm9zIjoid2ViIiwiaXQiOjEwNDAsInQiOiJYRjVDcitzUzIzYTFFaXJVZkxOaTgydWFSaitaWUFoV0Z4Tk90WUtCUW1uWVZuUDU0cTRaMUFnU3lwR3NDbXllNnJtWjA1UnU1NkswS1BHdlRjZjVWQT09In0==',
        'eyJ2IjoiNGhYNnhwMGNMOXc5KzVnRnkwNDErMDVYTTNQblgrOEZHMDhXTzZ2UXJEcVQrTUJxUHhaMUFWSXF5UFgyVlQzNCIsIm9zIjoid2ViIiwiaXQiOjk4MCwidCI6IkdEVEpLU3QwdmFxd21KQk1XRUwvQnU5TzlVQkRKODE0eXJyc3pRbmEzYndEQTJ4SjJlTC9XN1VKZVlIVUNMTDE0QlBya3M4ZnhmRE1OWUZlR2V4dGtRPT0ifQ',
        'eyJ2IjoiNGhYNnhwMGNMOXc5KzVnRnkwNDErMDVYTTNQblgrOEZHMDhXTzZ2UXJEcVQrTUJxUHhaMUFWSXF5UFgyVlQzNCIsIm9zIjoid2ViIiwiaXQiOjE5MjEsInQiOiJWbG1qcDJOcjE2bk1lSFMzL3ZLR1o5M2NhenZvNjRQczBaZ1pINlRJN3dnbFFUanFSbWRhOG5JZXJwTVRTU3ZOYjZMTU02U3d5T1VzMytnU1hIWVRpdz09In0=',
        'eyJ2IjoiNGhYNnhwMGNMOXc5KzVnRnkwNDErMDVYTTNQblgrOEZHMDhXTzZ2UXJEcVQrTUJxUHhaMUFWSXF5UFgyVlQzNCIsIm9zIjoid2ViIiwiaXQiOjExODEsInQiOiI4aTRzVkM3dnlENlJqQ2dacnhxblBLdG1ZYkYvRG93VlFMVmpydTNCYWhaK3hPcXB0cmpzU1RmY0NHeTZzSGFHa3FocSttazNaUzVJMDJ3SUEyOExIZz09In0='
    ]

    data = [
        '{"directType":"D","flightType":"OW","tripType":"D","arrCode":"KWE","sendCode":"SHA","departureDate":"2021-01-09","queryType":"","blackBox":"%s","channelCode":"MWEB","clientVersion":"1.7.2","versionCode":"17200"}'
        % random.choice(blackBox),
        '{"directType":"D","flightType":"OW","tripType":"D","arrCode":"SHA","sendCode":"KWE","departureDate":"2021-01-10","queryType":"","blackBox":"%s","channelCode":"MWEB","clientVersion":"1.7.2","versionCode":"17200"}'
        % random.choice(blackBox),
        '{"directType":"D","flightType":"OW","tripType":"D","arrCode":"SHA","sendCode":"SYX","departureDate":"2021-01-17","queryType":"","blackBox":"%s","channelCode":"MWEB","clientVersion":"1.7.2","versionCode":"17200"}'
        % random.choice(blackBox),
        '{"directType":"D","flightType":"OW","tripType":"D","arrCode":"CKG","sendCode":"SHA","departureDate":"2021-01-15","queryType":"","blackBox":"%s","channelCode":"MWEB","clientVersion":"1.7.2","versionCode":"17200"}'
        % random.choice(blackBox),
        '{"directType":"D","flightType":"OW","tripType":"D","arrCode":"SHA","sendCode":"CKG","departureDate":"2021-01-17","queryType":"","blackBox":"%s","channelCode":"MWEB","clientVersion":"1.7.2","versionCode":"17200"}'
        % random.choice(blackBox),
    ]
    for i in range(len(data)):
        requests_info(data[i])