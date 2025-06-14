import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.header import Header

# 邮件配置（从环境变量读取安全）
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.163.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 465))
EMAIL_USER = os.getenv('EMAIL_USER')  # 发件邮箱
EMAIL_PASS = os.getenv('EMAIL_PASS')  # 邮箱密码/授权码
TO_EMAIL = os.getenv('TO_EMAIL')     # 收件邮箱

def get_joke():
    """获取随机笑话API"""
    try:
        res = requests.get("https://v2.jokeapi.dev/joke/Any?type=twopart")
        data = res.json()
        if data['error'] is False:
            return f"{data['setup']}\n\n{data['delivery']}"
    except:
        pass
    return "今日笑话加载失败，程序员正在加班修复中..."

def get_poem():
    """获取随机诗歌API"""
    try:
        res = requests.get("https://www.poemist.com/api/v1/randompoems")
        poem = res.json()[0]
        return f"《{poem['title']}》\n\n{poem['content']}\n\n—— {poem['poet']['name']}"
    except:
        pass
    return "诗歌正在酝酿中，请明日再试..."

def send_email(content, subject="每日一笑一诗"):
    """发送邮件函数"""
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = Header(f"笑诗机器人 <{EMAIL_USER}>")
    msg['To'] = Header(TO_EMAIL)
    
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, [TO_EMAIL], msg.as_string())

def main_handler(event, context):
    # 生成内容
    joke = get_joke()
    poem = get_poem()
    content = f"🌟 今日份快乐送达 🌟\n\n😄 笑话一箩筐:\n{joke}\n\n📜 诗情画意:\n{poem}"
    
    # 发送邮件
    send_email(content)
    return {"status": "success", "message": "邮件已发送"}

# 本地测试用
if __name__ == "__main__":
    # 测试时直接设置环境变量
    os.environ['EMAIL_USER'] = 'your_email@163.com'
    os.environ['EMAIL_PASS'] = 'your_authorization_code'
    os.environ['TO_EMAIL'] = 'receiver@example.com'
    print(main_handler(None, None))
