import os
import smtplib
import requests
import logging
import socket
import traceback
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

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
    """获取笑话内容"""
    try:
        # 使用稳定的笑话API
        response = requests.get("https://official-joke-api.appspot.com/random_joke", timeout=8)
        response.raise_for_status()
        data = response.json()
        return data.get('setup', ''), data.get('punchline', '')
    except Exception as e:
        logger.error(f"笑话API错误: {str(e)}")
        return "生活本身就是最好的笑料", "请开怀一笑吧！😄"

def get_poem():
    """获取诗歌内容"""
    try:
        # 使用稳定的诗歌API
        response = requests.get("https://poetrydb.org/random/1", timeout=8)
        response.raise_for_status()
        poem = response.json()[0]
        return poem.get('title', '无题'), "\n".join(poem.get('lines', [])), poem.get('author', '未知作者')
    except Exception as e:
        logger.error(f"诗歌API错误: {str(e)}")
        return "诗意生活", "心灵自有诗意，\n请用心感受生活的美好。", "笑诗机器人"

def create_html_email(joke, poem):
    """创建精美的HTML邮件内容"""
    joke_setup, joke_punchline = joke
    poem_title, poem_content, poem_author = poem
    
    return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>每日一笑一诗</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; line-height: 1.6; background: #f7f9fc; padding: 20px; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #3498db, #2c3e50); padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .header-title {{ font-size: 28px; color: white; font-weight: bold; letter-spacing: 1px; margin-bottom: 10px; }}
        .header-subtitle {{ font-size: 16px; color: rgba(255,255,255,0.85); }}
        .content {{ padding: 30px; background: white; border-radius: 0 0 10px 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.05); }}
        .section {{ margin-bottom: 30px; }}
        .section:last-child {{ margin-bottom: 0; }}
        .section-header {{ display: flex; align-items: center; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #eee; }}
        .section-icon {{ font-size: 24px; margin-right: 10px; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; border-radius: 50%; }}
        .joke-section .section-icon {{ background: #f1c40f; color: white; }}
        .poem-section .section-icon {{ background: #9b59b6; color: white; }}
        .section-title {{ font-size: 22px; font-weight: bold; color: #2c3e50; }}
        .joke-content {{ background: #fffdf5; border-left: 4px solid #f1c40f; padding: 20px; border-radius: 0 8px 8px 0; }}
        .joke-setup {{ font-size: 18px; font-weight: 500; margin-bottom: 15px; color: #2c3e50; }}
        .joke-punchline {{ font-size: 20px; font-weight: bold; color: #e74c3c; }}
        .poem-content {{ background: #f9f4ff; border-left: 4px solid #9b59b6; padding: 20px; border-radius: 0 8px 8px 0; font-style: italic; }}
        .poem-title {{ font-size: 20px; font-weight: bold; margin-bottom: 15px; color: #8e44ad; }}
        .poem-author {{ text-align: right; font-weight: normal; color: #7f8c8d; margin-top: 10px; }}
        .poem-author::before {{ content: "——"; margin-right: 5px; }}
        .footer {{ text-align: center; padding: 20px 0; color: #7f8c8d; font-size: 14px; }}
        .robot-sign {{ display: inline-flex; align-items: center; background: #ecf0f1; padding: 6px 15px; border-radius: 20px; margin-top: 10px; }}
        .robot-icon {{ color: #3498db; margin-right: 5px; }}
        
        /* 响应式适配 */
        @media (max-width: 480px) {{
            .content {{ padding: 20px; }}
            .header {{ padding: 20px; }}
            .section-title {{ font-size: 20px; }}
            .joke-setup {{ font-size: 16px; }}
            .joke-punchline {{ font-size: 18px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-title">每日一笑一诗</div>
            <div class="header-subtitle">让笑声与诗意点亮您的一天</div>
        </div>
        
        <div class="content">
            <!-- 笑话部分 -->
            <div class="section joke-section">
                <div class="section-header">
                    <div class="section-icon">😂</div>
                    <div class="section-title">今日笑话</div>
                </div>
                <div class="joke-content">
                    <div class="joke-setup">{joke_setup}</div>
                    <div class="joke-punchline">{joke_punchline}</div>
                </div>
            </div>
            
            <!-- 诗歌部分 -->
            <div class="section poem-section">
                <div class="section-header">
                    <div class="section-icon">📜</div>
                    <div class="section-title">今日诗歌</div>
                </div>
                <div class="poem-content">
                    <div class="poem-title">《{poem_title}》</div>
                    <div class="poem-text">{poem_content}</div>
                    <div class="poem-author">{poem_author}</div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <div>来自GitHub机器人的温暖问候</div>
            <div class="robot-sign">
                <span class="robot-icon">🤖</span> 由Python驱动
            </div>
        </div>
    </div>
</body>
</html>
"""

def send_email():
    """发送邮件的主函数"""
    try:
        # 获取环境变量
        email_user = os.environ['EMAIL_USER']
        email_pass = os.environ['EMAIL_PASS']
        to_email = os.environ['TO_EMAIL']
        
        logger.info(f"准备发送邮件: {email_user} -> {to_email}")
        
        # 获取内容
        joke = get_joke()
        poem = get_poem()
        
        # 创建HTML邮件
        html_content = create_html_email(joke, poem)
        
        # 创建MIME消息（multipart格式）
        msg = MIMEMultipart('alternative')
        msg['Subject'] = '每日一笑一诗'
        msg['From'] = formataddr(('笑诗机器人', email_user))
        msg['To'] = to_email
        
        # 添加纯文本版本（备选）
        text_content = f"""每日一笑一诗\n\n😄 今日笑话: \n{joke[0]}\n{joke[1]}\n\n📜 今日诗歌: \n《{poem[0]}》\n{poem[1]}\n—— {poem[2]}\n\n来自GitHub机器人的温暖问候"""
        part1 = MIMEText(text_content, 'plain', 'utf-8')
        
        # 添加HTML版本
        part2 = MIMEText(html_content, 'html', 'utf-8')
        
        msg.attach(part1)
        msg.attach(part2)
        
        # 使用587端口+TLS连接
        logger.info("连接到QQ邮箱(端口587)使用STARTTLS...")
        
        # 创建SMTP连接
        server = smtplib.SMTP('smtp.qq.com', 587, timeout=15)
        server.ehlo()
        
        # 尝试通过STARTTLS升级连接
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
        
        # 关闭连接
        server.quit()
        logger.info("邮件发送成功！")
        return True
        
    except Exception as e:
        error_msg = f"邮件发送失败: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        return False

if __name__ == "__main__":
    send_email()
