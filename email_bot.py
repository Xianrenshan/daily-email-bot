import os
import smtplib
import requests
import logging
import time
import ssl
from email.mime.text import MIMEText
from email.header import Header

# 初始化日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    filename='email.log',
    filemode='w',
    encoding='utf-8'
)
logger = logging.getLogger()

def safe_api_call(url, retries=3, delay=1):
    """安全的API调用，带重试机制"""
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=8)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"API请求失败 (尝试 {attempt+1}/{retries}): {str(e)}")
            time.sleep(delay)
    return None

def get_joke():
    """获取笑话内容，带备选方案"""
    try:
        data = safe_api_call("https://v2.jokeapi.dev/joke/Any?type=twopart")
        if data and not data.get('error'):
            return f"{data.get('setup', '')}\n\n{data.get('delivery', '')}"
    except Exception:
        pass
    
    # 备选笑话API
    try:
        data = safe_api_call("https://official-joke-api.appspot.com/random_joke")
        if data:
            return f"{data.get('setup', '')}\n\n{data.get('punchline', '')}"
    except Exception:
        pass
    
    return "虽然今天笑话缺席，但快乐从不缺席！😄"

def get_poem():
    """获取诗歌内容，带备选方案"""
    try:
        # 更换更可靠的中文诗歌API
        data = safe_api_call("https://api.apiopen.top/api/sentences")
        if data and data.get('code') == 200:
            result = data.get('result', {})
            return f"{result.get('name', '')}\n\n{result.get('content', '')}"
    except Exception:
        pass
    
    # 备选诗歌API
    try:
        data = safe_api_call("https://poetrydb.org/random/1")
        if data and isinstance(data, list) and data[0]:
            poem = data[0]
            lines = "\n".join(poem.get('lines', []))
            return f"《{poem.get('title', '')}》\n\n{lines}\n\n—— {poem.get('author', '')}"
    except Exception:
        pass
    
    # 保底内容
    return "生活的诗篇，永远比纸上的文字更动人。🌈"

def connect_smtp(email_user, email_pass):
    """安全连接SMTP服务器"""
    try:
        logger.info("尝试加密方式连接QQ邮箱...")
        
        # 创建SSL上下文（使用高安全性配置）
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.set_ciphers('DEFAULT@SECLEVEL=2')
        
        # 使用安全连接
        with smtplib.SMTP_SSL('smtp.qq.com', 465, context=context, timeout=15) as server:
            server.login(email_user, email_pass)
            logger.info("QQ邮箱登录成功！")
            return server
    except ssl.SSLError as e:
        logger.error(f"SSL连接错误: {str(e)}")
    except Exception as e:
        logger.error(f"连接失败: {str(e)}")
    
    return None

def send_email():
    try:
        # 获取环境变量
        email_user = os.environ['EMAIL_USER']
        email_pass = os.environ['EMAIL_PASS']
        to_email = os.environ['TO_EMAIL']
        
        logger.info(f"准备发送邮件: {email_user} -> {to_email}")
        
        # 生成内容
        joke = get_joke()
        poem = get_poem()
        content = f"""
❤️ 每日一笑一诗 ❤️
--------------------
😄 今日笑话：
{joke}
--------------------
📜 今日诗歌：
{poem}
--------------------
来自GitHub机器人的温暖问候
"""
        # 创建邮件
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['Subject'] = Header('每日一笑一诗', 'utf-8')
        msg['From'] = f'笑诗机器人 <{email_user}>'
        msg['To'] = to_email
        
        # 创建安全连接
        smtp_server = connect_smtp(email_user, email_pass)
        if not smtp_server:
            raise ConnectionError("无法建立SMTP连接")
        
        # 发送邮件
        smtp_server.sendmail(email_user, [to_email], msg.as_string())
        logger.info("邮件发送成功！")
        
        return True
        
    except Exception as e:
        logger.error(f"邮件发送失败: {str(e)}")
        return False

if __name__ == "__main__":
    send_email()
