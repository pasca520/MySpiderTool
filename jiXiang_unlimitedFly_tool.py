# -*- coding: utf-8 -*-
import datetime
import smtplib
from configparser import ConfigParser
from email.mime.text import MIMEText

import requests


def sendemail(content):
    """
    :param content: 邮件内容
    :return: 发送状态
    """

    config = ConfigParser()
    config.read('config.ini', encoding='UTF-8')
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
        'versionCode': '17000',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
        'platformInfo': 'MWEB',
        'Content-Type': 'application/json;charset=UTF-8',
        'Accept': 'application/json, text/plain, */*',
        'channelCode': 'MWEB',
        'timeStamp': '1599066659285',
        'clientVersion': '1.7.0',
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
        if errorInfo =='查询过于频繁':
            print(time_stamp, errorInfo)
        else:
            flightInfoList = response.get("flightInfoList")
            for flightInfo in flightInfoList:
                for cabinFare in flightInfo['cabinFareList']:
                    if cabinFare['cabinCode'] == 'X':
                        # for airName in airNames:
                        carrierNoName = flightInfo.get('carrierNoName')
                        # if carrierNoName == airName:
                        arrCityName = flightInfo.get('arrCityName')
                        arrAirportName = flightInfo.get('arrAirportName')
                        arrTerm = flightInfo.get('arrTerm')
                        arrDateTime = flightInfo.get('arrDateTime')[-5:]
                        depCityName = flightInfo.get('depCityName')
                        depAirportName = flightInfo.get('depAirportName')
                        depTerm = flightInfo.get('depTerm')
                        depDateTime = flightInfo.get('depDateTime')[-5:]
                        cabinNumber = cabinFare['cabinNumber']
                        content = '航班:{}, 出发地: {}, 到达地: {}, 时间: {}~{}  '.format(
                            carrierNoName,
                            depCityName + depAirportName + depTerm,
                            arrCityName + arrAirportName + arrTerm,
                            depDateTime,
                            arrDateTime)
                        if cabinNumber == 'A':
                            content = content + '该航班可以兑换畅飞卡座位！'
                            sendemail(content)
                        elif int(cabinNumber) > 0:
                            content = content + '该航班剩余 %s 张畅飞卡座位！' % cabinNumber
                            sendemail(content)
                        else:
                            content = time_stamp + '  ' + content + '无畅飞卡座位'
                            print(content)
    except requests.exceptions.Timeout as e:
        print('请求超时：' + str(e.message))
    except requests.exceptions.HTTPError as e:
        print('http请求错误:' + str(e.message))


if __name__ == '__main__':
    data = ['{"arrCity":"\u4E0A\u6D77","sendCity":"\u4E4C\u9C81\u6728\u9F50","directType":"D","flightType":"OW","tripType":"D","arrCode":"SHA","sendCode":"URC","departureDate":"2020-10-11","returnDate":"2020-10-13","queryType":"","blackBox":"eyJ2IjoiNGhYNnhwMGNMOXc5KzVnRnkwNDErMDVYTTNQblgrOEZHMDhXTzZ2UXJEcVQrTUJxUHhaMUFWSXF5UFgyVlQzNCIsIm9zIjoid2ViIiwiaXQiOjE0ODIsInQiOiJNTk51YUJtQnRGU3J1MU9GOWJRTzdnRXdENzNHQkY1ZEZBekluclRKdGZMZWo2ZDRGOVJ4SUM2dGpIUThFOUNyV2txTzRZNWFHN1phb2gvOFR6ejdFUT09In0=","channelCode":"MWEB","clientVersion":"1.7.0","versionCode":"17000"}'
            ]
    for i in range(len(data)):
        requests_info(data[i])
