# -*- coding: utf-8 -*-
from time import sleep

import requests
from lxml import etree
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# 二维码登陆网页，没破解成功验证码登陆
def login_web():
    """
    :return:登陆的cookie
    """
    chromePath = '/Users/pasca/Desktop/github/MySpiderTool/chromedriver'
    options = ChromeOptions()  # 实例化一个ChromeOptions对象
    options.add_experimental_option('excludeSwitches', ['enable-automation'])  # 以键值对的形式加入参数
    driver = webdriver.Chrome(executable_path=chromePath, chrome_options=options)
    driver.get('https://account.dianping.com/login?redir=http%3A%2F%2Fwww.dianping.com%2F')
    timeout = WebDriverWait(driver, 10)  # 定义超时事件
    timeout.until(EC.frame_to_be_available_and_switch_to_it(
        (By.XPATH, '//*[@id="J_login_container"]/div/iframe')))  # 切换到 frame 框架
    timeout.until(EC.element_to_be_clickable((By.CLASS_NAME, 'qrcode-img')))  # 查看是否有扫码，验证是否登陆
    driver.switch_to.default_content()  # 切出框架
    sleep(10)
    # timeout.until(EC.element_to_be_clickable((By.CLASS_NAME, 'bottom-password-login'))).click()  # 点击 “账户登陆”
    # # timeout.until(EC.element_to_be_clickable((By.ID, 'tab-account'))).click().click()  # 点击手机密码登陆
    # driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    #     "source": """Object.defineProperty(navigator, 'webdriver', {get: () => undefined})""",
    # })
    #
    # phone = input('请输入手机号码:')
    # # 定位手机号码输入框
    # username = timeout.until(EC.presence_of_element_located((By.ID, 'mobile-number-textbox')))
    # for data in list(phone):
    #     username.send_keys(data)
    # sleep(1)
    # driver.find_element_by_xpath(r'//*[@id="send-number-button"]').click()
    # key = input('请输入验证码:')
    # driver.find_element_by_xpath(r'//*[@id="number-textbox"]').send_keys(key)
    # # 点击"获取验证码"
    # timeout.until(EC.presence_of_element_located((By.ID, 'send-number-button'))).click()
    # # 点击登录
    # sleep(random.uniform(0, 1))
    # driver.find_element_by_xpath('//button[@id="login-button-account"]').click()

    cookie = driver.get_cookies()
    cookies = {}
    for each in cookie:
        cookies[each['name']] = each['value']  # 处理cookies，得到正确格式
    return cookies


# 报名项目
def apply_project(offlineActivityId, branchId, applyPhone):
    data = {
        'offlineActivityId': offlineActivityId,
        'phoneNo': applyPhone,
        'shippingAddress': '',
        'extraCount': '',
        'birthdayStr': '',
        'email': '',
        'marryDayStr': '',
        'babyBirths': '',
        'pregnant': '',
        'marryStatus': '0',
        'comboId': '',
        'branchId': branchId,
        'usePassCard': '0',
        'passCardNo': '',
        'isShareSina': 'false',
        'isShareQQ': 'false'
    }

    response = requests.post('http://s.dianping.com/ajax/json/activity/offline/saveApplyInfo', headers=headers,
                             cookies=cookies,
                             data=data, verify=False).json()
    return response


# 获取分店 ID
def get_branch(offlineActivityId):
    data = {
        'offlineActivityId': offlineActivityId
    }
    url = 'http://s.dianping.com/ajax/json/activity/offline/loadApplyItem'

    response = requests.post(url=url, headers=headers,
                             cookies=cookies,
                             data=data, verify=False).json()
    code = response.get('code')
    msg = response.get('msg')
    html = msg.get('html')
    if code == 500:
        return '', '', html
    else:
        htmlData = etree.HTML(html)
        branchId = htmlData.xpath('//div/ul/li[2]/select/option[2]/@value')[
            0]  # 获取属性内容：/li/a/@herf ， 获取文本内容：/li/a/text()
        branchName = htmlData.xpath('//div/ul/li[2]/select/option[2]/text()')[
            0]  # 获取属性内容：/li/a/@herf ， 获取文本内容：/li/a/text()
        branchName = htmlData.xpath('//div/ul/li[2]/select/option[2]/text()')[
            0]  # 获取属性内容：/li/a/@herf ， 获取文本内容：/li/a/text()
        return branchId, branchName, '报名成功'


# 手机号
def get_phone(offlineActivityId):
    data = {
        'offlineActivityId': offlineActivityId
    }
    url = 'http://s.dianping.com/ajax/json/activity/offline/loadApplyItem'

    response = requests.post(url=url, headers=headers,
                             cookies=cookies,
                             data=data, verify=False).json()
    code = response.get('code')
    msg = response.get('msg')
    html = msg.get('html')
    if html == "您已经参与过了":
        return None
    else:
        htmlData = etree.HTML(html)
        applyPhone = htmlData.xpath('//div/ul/li/input/@value')[0]  # 获取属性内容：/li/a/@herf ， 获取文本内容：/li/a/text()
        return applyPhone

# 获取列表信息
def free_food_list():
    for page in range(1, 30):
        data = '{"cityId":"1","type":0,"mode":"","page":%s}' % page  # type1：美食，type2：丽人，type6：玩乐
        ajaxListURL = 'http://m.dianping.com/activity/static/pc/ajaxList'
        response = requests.post(url=ajaxListURL, headers=headers1,
                                 cookies=cookies,
                                 data=data, verify=False).json()
        if response.get('code') == 200:
            data = response.get('data')
            detail = data.get('detail')
            offlineActivityId = detail[0].get('offlineActivityId')  # 为了获取手机号码额外加的
            applyPhone = get_phone(offlineActivityId)
            for i in range(len(detail)):
                branchId = ''
                offlineActivityId = detail[i].get('offlineActivityId')
                detailUrl = detail[i].get('detailUrl')
                activityTitle = detail[i].get('activityTitle')
                applyResponse = apply_project(offlineActivityId, branchId, applyPhone)
                code = applyResponse.get('code')
                msg = applyResponse.get('msg')
                html = msg.get('html')
                if code == 200:
                    print(detailUrl, activityTitle, '报名成功!')
                elif code == 500 and html == "请选择分店":
                    branchId, branchName, infoRes = get_branch(offlineActivityId)
                    apply_project(offlineActivityId, branchId, applyPhone)
                    print(detailUrl, activityTitle, branchName, infoRes)
                elif code == 500 and msg == None:
                    print(detailUrl, activityTitle, '报名异常')
                else:
                    print(detailUrl, activityTitle, html)
        else:
            print(response.get('errorMsg'))


if __name__ == '__main__':
    cookies = login_web()
    headers1 = {
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36',
        'Content-Type': 'application/json',
        # 'Cookie': cookies,
        'Origin': 'http://s.dianping.com',
        'Referer': 'http://s.dianping.com/',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    headers = {
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Accept': 'application/json, text/javascript',
        'X-Requested-With': 'XMLHttpRequest',
        'X-Request': 'JSON',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8;',
        'Origin': 'http://s.dianping.com',
        # 'Cookie': cookies,
        # 'Referer': 'http://s.dianping.com/event/2123372828',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    free_food_list()