#coding=utf-8
import datetime
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
# smtplib用于邮件的发信动作
import smtplib
from email.mime.text import MIMEText
# email 用于构建邮件内容
from email.header import Header

# 用于构建邮件头
# 发信方的信息：发信邮箱，QQ 邮箱授权码
from_addr = 'your_email'
password = ''

# 收信方邮箱
to_addr = 'target_email'

# 发信服务器
smtp_server = 'smtp.qq.com'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
}

score_url = "https://yz.chsi.com.cn/apply/cjcx/cjcx.do"

def sendmail(msg):
    server = smtplib.SMTP_SSL(smtp_server)
    server.connect(smtp_server, 465)
    # 登录发信邮箱
    server.login(from_addr, password)
    # 发送邮件
    server.sendmail(from_addr, to_addr, msg.as_string())
    # 关闭服务器
    server.quit()

# 参数列表依次为----姓名 身份证号 考生编号 学校编号，请保证自己的姓名及身份证号不会填写错误，系统不会检查！
def main(xm = "",zjhm = "",ksbh = "",bkdwdm = ""):

    data = {
            "xm": xm,
            "zjhm": zjhm,
            "ksbh": ksbh,
            "bkdwdm": bkdwdm,
            "checkcode":""
        }

    session = requests.Session()
    score_page = session.post(url=score_url, headers=headers, data=data)
    score_soup = BeautifulSoup(score_page.text, 'lxml')
    # 使用UTC+8，方便在vps上部署
    timenow = datetime.datetime.utcnow() + datetime.timedelta(hours=8)

    try:

        # 成绩未出
        if score_soup.findAll(name="div", attrs={"class": "zx-no-answer"}):
            no_answer = score_soup.find("div", {"class": "zx-no-answer"}).text.strip()
            print("{0}------{1}".format(timenow.strftime("%Y-%m-%d %H:%M:%S"), str(no_answer).split("\n")[0]))

        # 成绩出了，以上div的内容应该会被隐藏，未考虑网站down掉的情况
        else:

            # 判断个人信息是否未填写或考生编号长度不符合要求，身份证号、姓名不检测
            if score_soup.findAll(name="form", attrs={"action": "/apply/cjcx/cjcx.do"}):
                print("个人信息参数为空或考生编号输入错误，请修改后重新运行代码！")
                # 邮箱正文内容，第一个参数为内容，第二个参数为格式(plain 为纯文本)，第三个参数为编码
                msg = MIMEText('输入信息错误', 'plain', 'utf-8')
                # 邮件头信息
                msg['From'] = Header(from_addr)
                msg['To'] = Header(to_addr)
                msg['Subject'] = Header('输入信息错误')
                # 开启发信服务，这里使用的是加密传输
                sendmail(msg)
                exit()

            # 应该是以table的形式呈现
            try:
                print("{0}------{1}\n".format(timenow.strftime("%Y-%m-%d %H:%M:%S"),"已查到成绩"))
                print(pd.read_html(score_page.text)[0])
                # 邮箱正文内容，第一个参数为内容，第二个参数为格式(plain 为纯文本)，第三个参数为编码
                msg = MIMEText('研招网出成绩啦', 'plain', 'utf-8')
                # 邮件头信息
                msg['From'] = Header(from_addr)
                msg['To'] = Header(to_addr)
                msg['Subject'] = Header('研招网出成绩啦')
                sendmail(msg)

            # 如果不是以table的形式呈现，直接查看
            except :
                score = score_soup.find("div", {"class": "container clearfix"}).text.strip()
                print("{0}------{1}\n".format(timenow.strftime("%Y-%m-%d %H:%M:%S"), "已查到成绩"))
                print(score)
                # 邮箱正文内容，第一个参数为内容，第二个参数为格式(plain 为纯文本)，第三个参数为编码
                msg = MIMEText('研招网出成绩啦', 'plain', 'utf-8')
                # 邮件头信息
                msg['From'] = Header(from_addr)
                msg['To'] = Header(to_addr)
                msg['Subject'] = Header('研招网出成绩啦')
                sendmail(msg)

            # 两种方式任意一种展示成绩后，结束程序
            finally:
                exit()

    except Exception as e :
        print("{0}------出现了问题：{1}\n".format(timenow.strftime("%Y-%m-%d %H:%M:%S"), e))
        exit()
if __name__ == '__main__':
    sumt = 0
    while True:
        main()
        if sumt != 86400:
            time.sleep(30)        # 设置爬虫爬取间隔，单位30S
            sumt = sumt+30
        else:
            msg = MIMEText('爬虫持续运行中！', 'plain', 'utf-8')
            # 邮件头信息
            msg['From'] = Header(from_addr)
            msg['To'] = Header(to_addr)
            msg['Subject'] = Header('爬虫持续运行中！')
            sendmail(msg)
            sumt = 0
            time.sleep(30)
            sumt =sumt+30


