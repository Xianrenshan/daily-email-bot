## 使用说明

1. Fork本仓库
2. 在仓库设置中设置Secrets：
   - `EMAIL_USER`: 发件邮箱地址
   - `EMAIL_PASS`: 邮箱密码或授权码
   - `TO_EMAIL`: 收件邮箱地址（可以设置为自己）
3. 默认的发送时间是每天UTC时间8:00（北京时间16:00），可以在`.github/workflows/email.yml`中修改cron表达式。

## 依赖

- 使用Python的requests库发送HTTP请求获取笑话和诗歌。
- 使用smtplib发送邮件。

## 感谢

笑话API：https://v2.jokeapi.dev/
诗歌API：https://api.apiopen.top/api/sentences
