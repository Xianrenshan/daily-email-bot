import os
import smtplib
import requests
import logging
import traceback
from email.mime.text import MIMEText
from email.header import Header

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('email.log', mode='w', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def safe_api_request(url, timeout=5):
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"API请求失败: {url} - {str(e)}")
        return None

def get_joke():
    data = safe_api_request("https://v2.jokeapi.dev/joke/Any?type=twopart")
    if data and not data.get('error'):
        return f"{data.get('setup', '')}\n\n{data.get('delivery', '')}"
    return "今日笑话加载失败 - 网络问题"

def get_poem():
    data = safe_api_request("https://www.poemist.com/api/v1/randompoems")
    if data and data[0]:
        poem = data[0]
        return f"《{poem.get('title', '')}》\n\n{poem.get('content', '')}\n\n—— {poem.get('poet', {}).get('name', '')}"
    return "诗歌加载失败 - 网络问题"

def send_email():
    try:
        # 获取环境变量（带默认值）
        email_user = os.getenv('EMAIL_USER', '')
        email_pass = os.getenv('EMAIL_PASS', '')
        to_email = os.getenv('TO_EMAIL', email_user or '')
        
        logger.info("===== 邮件机器人启动 =====")
        logger.info(f"发件人: {email_user or '[未设置]'}")
        logger.info(f"收件人: {to_email or '[未设置]'}")
        
        # 验证环境变量
        missing = []
        if not email_user: missing.append("EMAIL_USER")
        if not email_pass: missing.append("EMAIL_PASS")
        if not to_email: missing.append("TO_EMAIL")
        
        if missing:
            error_msg = f"缺少必需环境变量: {', '.join(missing)}"
            logger.error(error_msg)
            return False
        
        # 生成内容
        joke = get_joke()
        poem = get_poem()
        content = f"""
😄 今日笑话：
{joke}

📜 今日诗歌：
{poem}
        """
        
        # 创建邮件
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['Subject'] = Header('每日一笑一诗', 'utf-8')
        msg['From'] = Header(f'笑诗机器人 <{email_user}>', 'utf-8')
        msg['To'] = Header(to_email, 'utf-8')
        
        # QQ邮箱特殊配置
        logger.info("正在连接QQ SMTP服务器...")
        server = smtplib.SMTP_SSL('smtp.qq.com', 465, timeout=20)
        server.set_debuglevel(1)  # 输出详细SMTP日志
        
        logger.info("正在登录邮箱...")
        server.login(email_user, email_pass)
        
        logger.info("正在发送邮件...")
        server.sendmail(email_user, [to_email], msg.as_string())
        server.quit()
        
        logger.info("🎉 邮件发送成功！")
        return True
        
    except Exception as e:
        logger.error(f"❌ 邮件发送失败: {str(e)}")
        logger.error(traceback.format_exc())  # 记录完整错误堆栈
        return False
    finally:
        logger.info("===== 执行结束 =====")

if __name__ == "__main__":
    send_email()
