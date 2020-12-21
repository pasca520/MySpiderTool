# -*- coding: utf-8 -*-
import datetime
import random
import requests
import smtplib
from configparser import ConfigParser
from email.mime.text import MIMEText


def send_mail(content):
    """
    :param content: 邮件内容
    :return: 发送状态
    """

    config = ConfigParser()
    config.read('/Users/pasca/Desktop/github/MySpiderTool/config.ini', encoding='UTF-8')
    senderMail = config.get('mail', 'senderMail')
    authCode = config.get('mail', 'authCode')
    receiverMail = config.get('mail', 'receiverMail')

    senderMail = senderMail  # 发送者邮箱地址
    authCode = authCode  # 发送者 QQ邮箱授权码
    receiverMail = receiverMail  # 接收者邮箱地址
    subject = '赶紧兑换，有票出现了'  # 邮件主题
    # 邮件内容
    content = content
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
        print('邮件发送异常')
    finally:
        server.quit()


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
                    carrierNoName,
                    flightDate,
                    depCityName + depAirportName + depTerm,
                    arrCityName + arrAirportName + arrTerm,
                    depDateTime,
                    arrDateTime)
              # if cabinNumber == 'A' and carrierNoName in {'吉祥HO1107': '厦门',  '吉祥HO1105': '厦门',  '吉祥HO1198': '厦门',  '吉祥HO1108': '厦门'}:
                if cabinNumber == 'A':
                        content = content + '该航班可以兑换畅飞卡座位！'
                        send_mail(content)
                elif (cabinNumber == 'A' or int(cabinNumber) > 0):
                    content = content + '该航班剩余 %s 张畅飞卡座位！' % cabinNumber
                    send_mail(content)
                else:
                    content = time_stamp + '  ' + content + '余座: %s' % cabinNumber
                    print(content)


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
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
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

        errorInfo = response.get("errorInfo")
        if errorInfo == '查询过于频繁':
            print(time_stamp, errorInfo)
        else:
            flightInfoList = response.get("flightInfoList")
            
            parse_flight(flightInfoList, time_stamp)
    except requests.exceptions.Timeout as e:
        print('请求超时：' + str(e.message))
    except requests.exceptions.HTTPError as e:
        print('http请求错误:' + str(e.message))


if __name__ == '__main__':
    blackBox = ['eyJ2IjoiNGhYNnhwMGNMOXc5KzVnRnkwNDErMDVYTTNQblgrOEZHMDhXTzZ2UXJEcVQrTUJxUHhaMUFWSXF5UFgyVlQzNCIsIm9zIjoid2ViIiwiaXQiOjE1NTQsInQiOiJaRERRekhwbzR5ODZ5Uk9Ec1BYYS8wOFl5ekF2elN1TVFTbEJxU0JmajNpTFB1ODF2aVd0bkZEUzZmNWp3czN0czd0dXRpQzJFWitISzloMWlFbXBBZz09In0=',
                'eyJ2IjoiZ3YrYXhwV0tWTkFhWCtmcDUyMjdiYTkxRGw0OXVPRmRYT0lCWWxMVUlnSzhnRHRZN3QrcENMOGplZDZLTEZBaCIsIm9zIjoid2ViIiwiaXQiOjIwOTIsInQiOiJCdjdrQmp0Z2thZGw5WkxSbzdERk5wVnZlNURVT3ZuNFRtaUtrdS9VT1dIRnJ6czJmYXo3bEFmYkJLc2ZQYjZBbnJoTExEdWk4NERtMVZWNTFHazEwZz09In0=',
                'eyJ2IjoiNGhYNnhwMGNMOXc5KzVnRnkwNDErMDVYTTNQblgrOEZHMDhXTzZ2UXJEcVQrTUJxUHhaMUFWSXF5UFgyVlQzNCIsIm9zIjoid2ViIiwiaXQiOjMxOSwidCI6InlVRWN3cHFTVi9PNmU5UkpsQmxoclRoZm1wMlplb25ZL3JZM2xZSVlVMithL0hwbkZpempXT0ZxQTJWLzFaTk56eXVzUjR6QjFNYlh0a3czZUFFQUh3PT0ifQ==',
                'eyJ2IjoiNGhYNnhwMGNMOXc5KzVnRnkwNDErMDVYTTNQblgrOEZHMDhXTzZ2UXJEcVQrTUJxUHhaMUFWSXF5UFgyVlQzNCIsIm9zIjoid2ViIiwiaXQiOjgzOCwidCI6IkFrREd5WUdvN3JWNm9ROVhYK1o0cWtxeXN4U29zU1E5bVRZRTVLMmhLNklIZTdsdVJ6RlN1Rkh4S1lzVks1ZmtTMGM1ZEZUbDRUNXZkbU41eUJQa0R3PT0ifQ==',
                'eyJ2IjoiNGhYNnhwMGNMOXc5KzVnRnkwNDErMDVYTTNQblgrOEZHMDhXTzZ2UXJEcVQrTUJxUHhaMUFWSXF5UFgyVlQzNCIsIm9zIjoid2ViIiwiaXQiOjEwNDAsInQiOiJYRjVDcitzUzIzYTFFaXJVZkxOaTgydWFSaitaWUFoV0Z4Tk90WUtCUW1uWVZuUDU0cTRaMUFnU3lwR3NDbXllNnJtWjA1UnU1NkswS1BHdlRjZjVWQT09In0==',
                'eyJ2IjoiNGhYNnhwMGNMOXc5KzVnRnkwNDErMDVYTTNQblgrOEZHMDhXTzZ2UXJEcVQrTUJxUHhaMUFWSXF5UFgyVlQzNCIsIm9zIjoid2ViIiwiaXQiOjk4MCwidCI6IkdEVEpLU3QwdmFxd21KQk1XRUwvQnU5TzlVQkRKODE0eXJyc3pRbmEzYndEQTJ4SjJlTC9XN1VKZVlIVUNMTDE0QlBya3M4ZnhmRE1OWUZlR2V4dGtRPT0ifQ',
                'eyJ2IjoiNGhYNnhwMGNMOXc5KzVnRnkwNDErMDVYTTNQblgrOEZHMDhXTzZ2UXJEcVQrTUJxUHhaMUFWSXF5UFgyVlQzNCIsIm9zIjoid2ViIiwiaXQiOjE5MjEsInQiOiJWbG1qcDJOcjE2bk1lSFMzL3ZLR1o5M2NhenZvNjRQczBaZ1pINlRJN3dnbFFUanFSbWRhOG5JZXJwTVRTU3ZOYjZMTU02U3d5T1VzMytnU1hIWVRpdz09In0=',
                'eyJ2IjoiNGhYNnhwMGNMOXc5KzVnRnkwNDErMDVYTTNQblgrOEZHMDhXTzZ2UXJEcVQrTUJxUHhaMUFWSXF5UFgyVlQzNCIsIm9zIjoid2ViIiwiaXQiOjExODEsInQiOiI4aTRzVkM3dnlENlJqQ2dacnhxblBLdG1ZYkYvRG93VlFMVmpydTNCYWhaK3hPcXB0cmpzU1RmY0NHeTZzSGFHa3FocSttazNaUzVJMDJ3SUEyOExIZz09In0=']

    data = ['{"directType":"D","flightType":"OW","tripType":"D","arrCode":"YYA","sendCode":"SHA","departureDate":"2021-01-01","queryType":"","blackBox":"%s","channelCode":"MWEB","clientVersion":"1.7.2","versionCode":"17200"}' %random.choice(blackBox),
            '{"directType":"D","flightType":"OW","tripType":"D","arrCode":"SHA","sendCode":"YYA","departureDate":"2021-01-03","queryType":"","blackBox":"%s","channelCode":"MWEB","clientVersion":"1.7.2","versionCode":"17200"}' %random.choice(blackBox)]
    for i in range(len(data)):
        requests_info(data[i])
