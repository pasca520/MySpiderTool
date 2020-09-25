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
    data = [
        '{"directType":"D","flightType":"OW","tripType":"D","arrCode":"CSX","sendCode":"SHA","departureDate":"2020-09-30","returnDate":"2020-10-07","queryType":"","blackBox":"eyJ2IjoiNGhYNnhwMGNMOXc5KzVnRnkwNDErMDVYTTNQblgrOEZHMDhXTzZ2UXJEcVQrTUJxUHhaMUFWSXF5UFgyVlQzNCIsIm9zIjoid2ViIiwiaXQiOjU4NDAsInMiOjQsImQiOiJ7XCJwYXJ0bmVyXCI6XCJqeGhrXCIsXCJhcHBfbmFtZVwiOlwianhoa193ZWJcIixcInRva2VuX2lkXCI6XCJqeGhrLTE2MDAzMTEwNTM0NDMtOWI0NTkyNTMwOWY2ZlwiLFwiaVwiOlwibU1iMmYwZ3RpT1R4NVN6bnFUN0k3TXpVcnNNVDNPUXlmQnpWaWNsZWE3d0Vzd0Y0NU5zUjIvZFluZi9yVk9+angvVGxxRWNGQkRPWlVmdm5CUnNvekFzYW5BVmhBREd0bFU3RmRkbng1RTE3VTgxSVc3Uk9FeW83T3dMS2c3SjdQdmhJRnkyVWdaNnFYdXFYOURaUFBldkJ5TG9UZ2dkeGJYZUJ1ZzBWbjFVL3NXL2FSQ2hhVUpUMFJmNDBaaGFNckJySk9vVGUzWi9NUnR5L3RVM3V4flczL0xjUnBGc2lKVDhJZkE4TzVSQkxzVjlwTlVyckNNaXdmY3RkdHVFazBzWH51UGRtTFpubVFtMU5pV0NVSmY2bEJPSTN6ODRJRGQzM3VqVkw2OXd3Zll2WGl6MDBjSmU1eExlVnNaU2tUNEx3ZGk1VTB+NlM5RUV+d3JvaEZZMEF6cEg5Wmh+RVhkNnZQYTQvTDRWVzc1N2JZNGozMFdrNlV3MXBNMjBYfklpTVZvSkdjSHJ0VWxNYzRsSDdCdUN+anNLM3M3SWExTU9uOVRVd0czNTBBUHRMZGhYNH51eFZTYVdyemtoRVwiLFwialwiOlwidU5rWDZ1bTdDcU0zRkFldX40SzJXRDNLREFUWHgzRGlvQmJHYkM0QTN+UUlVUE00aHYyZ0hrVXBLY0F2V1V2WVdISHNmME9TazhocFpuSXl4SW1iUGltZ1hPbFZMQWpFRVZEN0ZoQ3N0dmEydEl3UDlHVG9FaGVJVlVwRzVNQk40VGY1cnF2cmpHVTBoRE9VSzNTdDRqU2NFRUxVcUdrVGc4bHFnUEU2UlJCR0NTbHgzaWsxQkxrMndCSDJLbkZjUVozVHE0RS92TFR+aExXYU1hcEE3QmEzSExZNzZ5eFE0eTEybGtaSm51aGVNWXZBOGc4NHlYVlFrME9TM2F3WnE2fkxpRktMd2RVcFZqMX5zTjZtWVc9PVwiLFwia1wiOlwiYm81b29mV05Db0N6emdVUkNxcmViRXU5RDBqdm1aR2lDclFHRkZhZDNNUFZUQ1l4UTY5blVVazAyTHRKeWZLWWhvbFNKUW5rMUhPNUtCOVpnS3FRNnBqTXE4VTJ+dXRIRENOTXJ+OHZNL3J6OW1lbWg0a1JMNElLTDhNcGVtOWNGR0FTVUFJMkdCRVhlUDZDdEdmMWZYRjRiZzdZZ3I5ZEZRekY0WjFBNnN4RnV2RWxUenhoOVdnVFVudTFnaWl+M0tGZUN4UXFQUnJ3WXd5QnRzaTIvVGtMNkdjQ3d+UVBuajRRUkZVMUEzWHJxfmlPY3FqNjBVYzg5enJ2MlFVfkdUVXBTcE9mUGFoeDBmT0J+eVM4ZllteW54RlpFWWVCQXd6M2x6RWZUVHdRcFFkMWdPNzFyNG14U1ROZjhHbWp4bGFINDN3bG1aQ1pOTEVXSVMveTNVcE1Eb0EvQmE1N1V0Vn56bFdISkZGY0dtQjBLNmtwV1dnVGpXRn5JZk1oTXZOTGV6NGJPbS8zV21KYmRuZW9+SlBkNWxCazlSWWdhTEhma1lqZ0pIMkVOblU0MHhIOHhCenlTaERnanJtc29pUG1hTmNtVFZPUlRaU1ZaSEhWVU5ob0p5Q2xlUmxIcms3dy9NVnlTMG9tYVlpUUVoMUhCeHVQV0s4OU5Ua0Vod1JNOWFXSnlUOE1MOWVHflhjc1VxMXBlRWRRfkVOT2o3OTJaWTJIdTVYWHRWMn5mbmgyNjVuZ1E2ekxQc1htcWd3OEZyb2hTVVlpWVptMnREa3V6b1M3UDZua2VocFFGOVVkd1RBdWR0UExYN2t2aVUvVVZVcVFRQnNDeHhBM2tPMUN6OEE5MUZlU3Zqdng1c3gyVWM0Y2pqQjB2Lzl4QlVFUHg0U2duMnAvTm5BQVRVWGp2SnN6ZXIyM09VY0tDNDdaR0V+Nk4walg3alcwMDdQVG1VaFFUVVR6UmVQSVpIdUpyfnJPNEp1dzVXTEhJM3gwZzRxZzJXVUVPNzRHdGcwd1gwSEx5bEhsNk5yNHN5YVhQb3g2MWZtUkpJVlRzOENVdFZ6SHVCMD1cIixcImxcIjpcIkxkdlJwcjU3VEVtM2xaOC9NcVh+clpHeWZZVVlmUkpPdUYxZ1ZLT01RSzBGMjR5RzZ1SlFpL3J5SzV1TVNib3VPaEpVZHJuV0xhRjlaeVczUUE4Yk1LSGFPZW0ybldoODUzaWhpSENBdmVlL1AxOWJLT3RncmUzclNVMUtCZHB5ZnBDSS9NcUl3SjMvYzNhdXc1T3U1ODZDfmE3QXl2cmQ0bHhDOGxnbkJPNU53OTNSL1pCUmpET3ZkOG9Kan5OSX5nQXBGRmNxNjRiLzlWUVRBSGJSL2NyeXdRZFdLY2lKd2l3bXpEOWw5SFc9XCIsXCJvXCI6XCJqWFJ+ejVYTnpwYURtaW9nNnlOV3VtSk9TOTltUGZSMH5SYmlETmNMUFV2T0V2fk5Cbmd5MVNMcThDUTlrNmxmM09qUlVBdDMvenpqQ1RxM28zVVEzSTk5UXI1cUM2aUc3WkVDS3VZRGJFTk41QlFXc09vczB5L29MUktYeWx3TnN0YTVWWUQ2RzFmZnlTVVdXQmZTWjVnTDA4eVVTSDg3OWJ3Qnhsb0RENkVCUEhKdkFBRkNGc0ZBR25FV35IUDhCWEs5M1N6dk82bTdqblJCbGlFT00zQ2xJUnJDWTFjTUxRaGQwMUozSE8yVE1ib1Evd01HdUZqZE9ZNm9LTjEwYXMzMGJkd3h0UDhEdXh3NE9ZdTgvODlLUXQ4QkhvZTdUQnZ2fm0xZWJDL2xJM1E5OGJqc1kyRU5UMHl1cUdSZUlUWHVUMEUvMXNPaWp3NkJtSUxWcDI2VGRNUVBjOENPN3dia2Y3fi9pSHE4cktrQ2d3QU1ZYnp4MTJPZXlDUXJnekN6V3AzWmZXZTVQRmRqYnRyd2xXPT1cIixcImZcIjpcImMxY3VhOFFiT3NQY0daYUtESjhpUVc9PVwiLFwidVwiOlwiMTYwMDMxMTA1NDE2M2RkbGNsbWJrZ2ZtZGNiaGNtbmduXCIsXCJlXCI6XCJIMjZ6dkwvQmlzR0ZDNXo1andOV0dSQ0tza1dxMnp0dG5IZ2dCV3NmNnYxTlhyeHZkY2ZmazNzOGJWNXg5TXRYM25ZTkpNTHJiaXhSc0xva0VuVFJ4ZXJLYjI2dHVrYzJ1cWNUZ0dKeG5Qdz1cIixcInZcIjpcIjRoWDZ4cDBjTDl3OSs1Z0Z5MDQxKzA1WE0zUG5YKzhGRzA4V082dlFyRHFUK01CcVB4WjFBVklxeVBYMlZUMzRcIixcImlkZlwiOlwiMTYwMDMxMTA1NDE2My0xNTA2OTAxNTI1N1wiLFwid1wiOlwiMTR3TTNGSzNPVW9PY0hVRTNoalR4U3BsZzI5TEIvUWZQY3FMYlNrZjNtRVRZYzdyR0U5NnlSdHZ0V3ExV0YwfnFDemYvcGxvekRzOTZNRmhLdWJ4SER6dEVJYllvdzVja3BKRVBEajNveWk9XCIsXCJjdFwiOlwiNXFLeGJPNWtUcUdoV1p6S004Q256Rz09XCJ9In0=","ffpId":12129161,"ffpCardNo":"2756968583","loginKeyInfo":"5F4D8A34D4C63D7FF65B5569503E28C4","channelCode":"MWEB","clientVersion":"1.7.0","versionCode":"17000"}',
        '{"directType":"D","flightType":"OW","tripType":"D","arrCode":"YYA","sendCode":"SHA","departureDate":"2020-09-30","returnDate":"2020-10-07","queryType":"","blackBox":"eyJ2IjoiNGhYNnhwMGNMOXc5KzVnRnkwNDErMDVYTTNQblgrOEZHMDhXTzZ2UXJEcVQrTUJxUHhaMUFWSXF5UFgyVlQzNCIsIm9zIjoid2ViIiwiaXQiOjUzNjksInQiOiI2OGJCV003ekpPSjFrRW04aFVmRHRDckZORzU4bHpiR0RFc1h1VXdJZytWSFhwOWNqMW9Ia1I0b2Y1MnpDelJuU1NHa1Z2aTJYM2tQb2UwTWNXKzAwQT09In0=","ffpId":12129161,"ffpCardNo":"2756968583","loginKeyInfo":"5F4D8A34D4C63D7FF65B5569503E28C4","channelCode":"MWEB","clientVersion":"1.7.0","versionCode":"17000"}']

    for i in range(len(data)):
        requests_info(data[i])
