import os
import smtplib
import requests
import logging
import socket
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

def get_joke():
    """获取笑话内容（使用可靠API）"""
    try:
        # 使用稳定可靠的笑话API
        response = requests.get("https://official-joke-api.appspot.com/random_joke", timeout=8)
        response.raise_for_status()
        data = response.json()
        return f"{data.get('setup', '')}\n\n{data.get('punchline', '')}"
    except Exception as e:
        logger.error(f"笑话API错误: {str(e)}")
        return "生活本身就是最好的笑料，请开怀一笑吧！😄"

def get_poem():
    """获取诗歌内容（使用可靠API）"""
    try:
        # 使用稳定的诗歌API
        response = requests.get("https://poetrydb.org/random/1", timeout=8)
        response.raise_for_status()
        poem = response.json()[0]
        lines = "\n".join(poem.get('lines', []))
        return f"《{poem.get('title', '')}》\n\n{lines}\n\n—— {poem.get('author', '')}"
    except Exception as e:
        logger.error(f"诗歌API错误: {str(e)}")
        return "心灵自有诗意，请用心感受生活的美好。📜"

def send_email():
    """发送邮件的主函数"""
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
        
        # 使用587端口+TLS连接（关键修改！）
        logger.info("连接到QQ邮箱(端口587)使用STARTTLS...")
        
        # 创建非加密连接
        server = smtplib.SMTP('smtp.qq.com', 587, timeout=15)
        
        # 尝试通过STARTTLS升级连接
        server.ehlo()
        if not server.has_extn('STARTTLS'):
            raise RuntimeError("SMTP服务器不支持STARTTLS")
        
        # 启动安全传输
        server.starttls()
        server.ehlo()
        
        # 登录和发送
        logger.info("登录邮箱...")
        server.login(email_user, email_pass)
        logger.info("发送邮件...")
        server.sendmail(email_user, [to_email], msg.as_string())
        
        # 优雅关闭
        server.quit()
        logger.info("邮件发送成功！")
        return True
        
    except socket.gaierror:
        logger.error("无法解析smtp.qq.com，请检查DNS设置")
    except smtplib.SMTPAuthenticationError:
        logger.error("邮箱认证失败！请检查邮箱和授权码")
        logger.error("提示：QQ邮箱需使用授权码而非密码")
    except Exception as e:
        logger.error(f"邮件发送失败: {str(e)}")
        return False

if __name__ == "__main__":
    send_email()
