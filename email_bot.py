# email_bot.py
import os
import smtplib
import requests
from email.mime.text import MIMEText

def get_joke():
    try:
        res = requests.get("https://v2.jokeapi.dev/joke/Any?type=twopart")
        data = res.json()
        return f"{data['setup']}\n\n{data['delivery']}"
    except:
        return "今日笑话加载失败"

def get_poem():
    try:
        res = requests.get("https://www.poemist.com/api/v1/randompoems")
        poem = res.json()[0]
        return f"《{poem['title']}》\n\n{poem['content']}\n\n—— {poem['poet']['name']}"
    except:
        return "诗歌加载失败"

def send_email():
    # 获取环境变量
    email_user = os.environ['EMAIL_USER']
    email_pass = os.environ['EMAIL_PASS']
    to_email = os.environ['TO_EMAIL']
    
    # 生成内容
    content = f"😄 今日笑话:\n{get_joke()}\n\n📜 今日诗歌:\n{get_poem()}"
    
    # 发送邮件
    msg = MIMEText(content)
    msg['Subject'] = '每日一笑一诗'
    msg['From'] = email_user
    msg['To'] = to_email
    
    with smtplib.SMTP_SSL('smtp.qq.com', 465) as server:
        server.login(email_user, email_pass)
        server.sendmail(email_user, [to_email], msg.as_string())

if __name__ == "__main__":
    send_email()
