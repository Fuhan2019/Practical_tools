# -*- coding: utf-8 -*-

"""
以下代码以《计算机二级的报名动态》公告页面的监控案例来说明如何进行网页最新信息监控，并对比过滤掉本地已获取的信息，
将页面上的最新通知公告信息标题通过邮件及时发送到接收者的邮箱。【只会提示新信息，log中已经存在的信息不会重复提醒】

* 可以扩展到监控学校官网通知页面、各类考试信息通知页面、买票网站、爱豆微博、一切你关心的页面的最新信息，免去自己频繁访问网页的烦恼。作者实用感受：很香！
建议在本地windows配置定时运行计划任务，可参考博客：https://blog.csdn.net/artificial_idiots/article/details/108570387

当前只有1个任务task_1，可添加多个任务，作为task_n：
1-【计算机二级考试动态】
"""

import requests
from bs4 import BeautifulSoup
import time


def task_1():
    name = '【计算机二级考试动态】'
    print(f'开始检测{name}信息更新')
    # 获取网页
    # Headers 里面大小写均可
    url = 'http://ncre.neea.edu.cn/html1/category/1507/872-1.htm'  # 要监控的页面的网址
    headers = {'Users-Agent': "Mozilla/5.0(X11;Ubuntu;Linux )x86_64;rv:52.0)Gecko/20100101 Firefox/52.0"}
    data = requests.get(url, headers=headers)
    data.encoding = 'utf-8'  # 将编码格式改为utf - 8

    # 解析数据
    soup = BeautifulSoup(data.text, 'html.parser')
    news = soup.select('#ReportIDname > a')  # 目标内容的位置，审查，右键，copy，selector

    # 设置预警信息 - 通过检查已保存的历史信息日志，避免定时运行重复提醒，实现仅提醒最新信息
    contents = ''
    with open("task_1.log", "a+", encoding='utf-8', errors='ignore') as f:
        f.seek(0)  # 将指针重新定位到文件头才能读出内容
        a = f.read()
        for tag in news:
            content = tag.text
            if True:  # 网页内容监控条件设置 & (【所有】更新的内容)
                # 去除已有信息，只提示不在列表中的
                if content not in a:
                    contents = contents + '\n' + content  # 记录到要提醒的内容
                    # 记录到日志，下次不再重复提醒，加上记录时间
                    f.write('\n' + content + '  ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))
    # print(contents)

    if len(contents) == 0:
        contents = ''
        print(f'对比本地task_1.log日志，{name}信息无更新\n')
    else:
        contents = f'\n{name}页面最新信息：\n' + contents + '\n\n'
    return contents


"""运行各任务，获取最新信息"""
# 第一个任务
try:
    content_1 = task_1()
except:
    content_1 = '\n\n【计算机二级考试动态】信息获取失败 ！\n\n'


contents = content_1  # 这里是所有的要提醒的信息
print(contents)

"""邮件-短信聚合交叉提醒模块"""
email = True

# 发送邮件提醒，需要先在邮箱设置中开通SMTP发件功能
import smtplib
from email.mime.text import MIMEText
from email.header import Header

if (len(contents) > 0) & (email is True):
    mail_host = "smtp.qq.com"  # 设置服务器
    mail_user = "666666"  # 用户名-你的邮箱账号，如果是QQ邮箱就是QQ号
    mail_pass = "fslfahfahkjlehr"  # 口令-开通SMTP时获得的口令，用来替代邮箱密码
    sender = '666666@qq.com'  # 发件人名称
    receivers = ['88888888@qq.com']  # 信息接收者的收件地址

    text = '------News!【你关注的网页】有如下更新信息：------\n\n' + contents  # 设置推送内容
    message = MIMEText(text, 'plain', 'utf-8')
    message['From'] = Header("Python-信息服务", 'utf-8')
    message['To'] = Header("Administrator", 'utf-8')

    subject = 'Python-Fu通知： 您所关注的网页有最新信息动态'
    message['Subject'] = Header(subject, 'utf-8')

    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mail_host, 587)  # QQ邮箱发送邮件服务器：smtp.qq.com，使用SSL，端口号465(不可用)或587(可用)，25无加密端口（可用）
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("邮件发送成功")
    except smtplib.SMTPException:
        print('邮件发送失败，换端口再次尝试')
        try:
            smtpObj = smtplib.SMTP()
            smtpObj.connect(mail_host, 25)  # 换25端口尝试
            smtpObj.login(mail_user, mail_pass)
            smtpObj.sendmail(sender, receivers, message.as_string())
            print("邮件发送成功")
        except smtplib.SMTPException:
            print("Error: 无法发送邮件。“邮件提醒”可能配置不正确")
            try:
                # 需要自行注册twilio账号并配置获得免费的token，具体方法百度
                from twilio.rest import Client

                # 当邮件无法发送时，发送短信提醒。仅适用于少量文本的提醒
                account_sid = 'xxxxxxxxxxxxxxxx'  # 填入你注册时产生的账号
                auth_token = 'xxxxxxxxxxxxxxxxx'  # 填入你注册时分配的token
                client = Client(account_sid, auth_token)

                text = f'"【你关注的网页】最新信息"监测任务有信息更新，但邮件提醒无法发送!'
                message = client.messages.create(
                    body=text,
                    from_='+12xxxxxxxx',  # 填入你申请的虚拟号码
                    to='+86xxxxxxxx'  # 填入你自己的号码【需要提前在twilio中认证】
                )
                print("短信发送成功")
            except:
                print("短信无法发送，请检查配置")

