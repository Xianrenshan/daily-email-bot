import os
import smtplib
import requests
import logging
from email.mime.text import MIMEText
from email.header import Header

# 配置日志（更简洁的方式）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    filename='email.log',
    filemode='w',
    encoding='utf-8'
)
logger = logging.getLogger()

def get_joke():
    """简化笑话获取函数"""
    try:
        res = requests.get("https://v2.jokeapi.dev/joke/Any?type=twopart", timeout=10)
        data = res.json()
        return f"{data.get('setup', '')}\n\n{data.get('delivery', '')}"
    except Exception as e:
        logger.error(f"笑话API错误: {str(e)}")
        return "今日笑话加载失败"

def get_poem():
    """简化诗歌获取函数"""
    try:
        res = requests.get("https://www.poemist.com/api/v1/randompoems", timeout=10)
        poem = res.json()[0]
        return f"《{poem.get('title', '')}》\n\n{poem.get('content', '')}\n\n—— {poem.get('poet', {}).get('name', '')}"
    except Exception as e:
        logger.error(f"诗歌API错误: {str(e)}")
        return "诗歌加载失败"

def send_email():
    """QQ邮箱优化版发送函数"""
    try:
        # 获取环境变量
        email_user = os.environ['EMAIL_USER']
        email_pass = os.environ['EMAIL_PASS']
        to_email = os.environ['TO_EMAIL']
        
        logger.info(f"准备发送邮件: {email_user} -> {to_email}")
        
        # 创建邮件内容
        content = f"😄 今日笑话:\n{get_joke()}\n\n📜 今日诗歌:\n{get_poem()}"
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['Subject'] = Header('每日一笑一诗', 'utf-8')
        msg['From'] = Header(f'笑诗机器人 <{email_user}>', 'utf-8')
        msg['To'] = to_email
        
        # 连接并发送邮件
        with smtplib.SMTP_SSL('smtp.qq.com', 465) as server:
            server.login(email_user, email_pass)
            server.sendmail(email_user, [to_email], msg.as_string())
        
        logger.info("邮件发送成功!")
        return True
        
    except KeyError as e:
        logger.error(f"缺失环境变量: {str(e)}")
    except smtplib.SMTPAuthenticationError:
        logger.error("QQ邮箱认证失败: 请确认邮箱和授权码正确")
    except Exception as e:
        logger.error(f"邮件发送失败: {str(e)}")
    
    return False

if __name__ == "__main__":
    send_email()
    # 添加完成标记，方便工作流检测
    print("SCRIPT EXECUTION COMPLETED")
