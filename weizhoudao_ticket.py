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


def requests_info():
    cookies = {
        'PHPSESSID': 'gq110k77367s9hjkesn2ma2h28',
        'x_flag': 'MTYx6wMTAxNjI5NV85NTA5Nl83MjYwMg%3D%3Dj4',
        'Hm_lvt_a57a71f129fdc25ec69051711972a745': '1601016298',
        'Hm_lpvt_a57a71f129fdc25ec69051711972a745': '1601016349',
        'acw_tc': '76b20f4416010163616006406e1910f4d322e28ef502ff8a44db4b0fd97de1',
        'x_flag_day': 'MTY2zwMTAxNjM2MV8xMTk0OTlfNzU0MDc%3Duw',
        'v__ship_0': '1',

        'v___0': '1',
        'Hm_lvt_a95a8cb7297d8df3640e6787e2d6a5fa': '1601016365',
        'Hm_lpvt_a95a8cb7297d8df3640e6787e2d6a5fa': '1601016365',
        'SL_GWPT_Show_Hide_tmp': '1',
        'SL_wptGlobTipTmp': '1',
        'vistor_source_des_': '%E7%AB%99%E5%86%85%E8%B7%B3%E8%BD%AC',
        'vistorRecordVistorinfo_MTYx6wMTAxNjI5NV85NTA5Nl83MjYwMg__j4': 'a%3A4%3A%7Bs%3A9%3A%22record_id%22%3Bs%3A8%3A%2210025290%22%3Bs%3A11%3A%22record_time%22%3Bi%3A1601016379%3Bs%3A10%3A%22source_des%22%3Bs%3A12%3A%22%E7%AB%99%E5%86%85%E8%B7%B3%E8%BD%AC%22%3Bs%3A9%3A%22is_record%22%3Bi%3A0%3B%7D',
        'v__ship_line_0': '1'
    }

    headers = {
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://m.laiu8.cn',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://m.laiu8.cn/ship/line?&prevDate=2020-10-08&nextDate=2020-09-26&prevLimit=2020-09-25&nextLimit=2020-10-01&reverse=0&departPort=17&arrivalPort=16',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }

    data = {
        'prevDate': '2020-10-08',
        'nextDate': '2020-09-26',
        'prevLimit': '2020-09-25',
        'nextLimit': '2020-10-01',
        'reverse': '0',
        'departPort': '17',
        'arrivalPort': '16',
        'channel': '',
        'pick': '0'
    }



    time_stamp = datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S')
    try:
        response = requests.post('https://m.laiu8.cn/ship/lineEnter', headers=headers, cookies=cookies,
                                 data=data).json()
        msg = response.get('msg')
        if msg == '抱歉，系统23:45-05:00进行维护!':
            content = time_stamp + '  ' + msg
            print(content)
        else:
            line_list = response.get('line_list')
            for i in range(len(line_list)):
                code = line_list[i].get('code')
                lineName = line_list[i].get('lineName')
                plannedDepartureDate = line_list[i].get('plannedDepartureDate')
                plannedDepartureTime = line_list[i].get('plannedDepartureTime')
                run_time = line_list[i].get('run_time')
                sale_num = line_list[i].get('sale_num')
                if code != 'WB03':
                    content = '船号:{}, 行程:{}, 时间:{} {}, 耗时:{}, 余票：{}'.format(code, lineName, plannedDepartureDate,
                                                                            plannedDepartureTime, run_time, sale_num)
                    if sale_num > 0:
                        content = content + '该船有位置了！'
                        sendemail(content)
                    else:
                        content = time_stamp + '  ' + content + '  该船没有位置'
                        print(content)
    except requests.exceptions.Timeout as e:
        print('请求超时：' + str(e.message))
    except requests.exceptions.HTTPError as e:
        print('http请求错误:' + str(e.message))


if __name__ == '__main__':
    requests_info()
