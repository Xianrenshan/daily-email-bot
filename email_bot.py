import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.header import Header  # 重要：添加Header解决编码问题
import logging  # 添加日志记录
import traceback  # 获取详细错误信息

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_joke():
    try:
        res = requests.get("https://v2.jokeapi.dev/joke/Any?type=twopart", timeout=10)
        data = res.json()
        if not data.get('error', True):
            return f"{data.get('setup', '')}\n\n{data.get('delivery', '')}"
        return "今日笑话加载失败 - API返回错误"
    except Exception as e:
        logger.error(f"获取笑话失败: {str(e)}")
        return "今日笑话加载失败"

def get_poem():
    try:
        res = requests.get("https://www.poemist.com/api/v1/randompoems", timeout=10)
        poem = res.json()[0]
        return f"《{poem.get('title', '')}》\n\n{poem.get('content', '')}\n\n—— {poem.get('poet', {}).get('name', '')}"
    except Exception as e:
        logger.error(f"获取诗歌失败: {str(e)}")
        return "诗歌加载失败"

def send_email():
    try:
        # 获取环境变量
        email_user = os.environ['EMAIL_USER']
        email_pass = os.environ['EMAIL_PASS']
        to_email = os.environ['TO_EMAIL']
        
        logger.info(f"尝试发送邮件: {email_user} -> {to_email}")
        
        # 生成内容
        joke = get_joke()
        poem = get_poem()
        content = f"😄 今日笑话:\n{joke}\n\n📜 今日诗歌:\n{poem}"
        
        # 发送邮件 (关键修改部分)
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['Subject'] = Header('每日一笑一诗', 'utf-8')  # 中文主题编码
        msg['From'] = Header(f'笑诗机器人 <{email_user}>', 'utf-8')  # QQ要求带发件人名称
        msg['To'] = Header(to_email, 'utf-8')
        
        # QQ邮箱特殊配置
        server = smtplib.SMTP_SSL('smtp.qq.com', 465)
        server.set_debuglevel(1)  # 启用调试信息输出
        server.login(email_user, email_pass)
        server.sendmail(email_user, [to_email], msg.as_string())
        logger.info("邮件发送成功!")
        
        # 重要：必须显式关闭连接
        server.quit()
        
    except KeyError as e:
        logger.error(f"缺失环境变量: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"邮件发送失败: {str(e)}")
        logger.error(traceback.format_exc())  # 输出详细错误堆栈
        raise

if __name__ == "__main__":
    send_email()
