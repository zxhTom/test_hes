import smtplib, ssl
from email.mime.text import MIMEText

# 配置信息
smtp_server = "smtp.163.com"
port = 465  # SSL端口
sender_email = "zxhtom13141@163.com"
password = "MKvK43eH7C8dP4qu"  # 授权码，不是邮箱密码
receiver_email = "870775401@qq.com"

# 创建邮件
message = MIMEText("邮件正文内容", "plain", "utf-8")
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = "邮件主题"

# try:
#     with smtplib.SMTP_SSL(smtp_server, port) as server:
#         server.local_hostname = "localhost"
#         server.set_debuglevel(1)
#         server.login(sender_email, password)
#         server.sendmail(sender_email, receiver_email, message.as_string())
#     print("邮件发送成功！")
# except Exception as e:
#     print(f"发送失败: {e}")


sender = "zxhtom13141@163.com"
password = "MKvK43eH7C8dP4qu"
receiver = "870775401@qq.com"

msg = MIMEText("TLS 测试", "plain", "utf-8")
msg["Subject"] = "TLS 测试"
msg["From"] = sender
msg["To"] = receiver

context = ssl.create_default_context()
context.set_ciphers("HIGH:!aNULL:!eNULL")  # 强制安全套件

# server = smtplib.SMTP_SSL("smtp.163.com", 465, context=context)
# server.set_debuglevel(1)
# server.login(sender, password)
# server.sendmail(sender, [receiver], msg.as_string())
# server.quit()


print("hhhh")
server = smtplib.SMTP("smtp.163.com", 587)
server.ehlo("zxhtom")
server.starttls(context=ssl.create_default_context())
server.login(sender, password)
server.sendmail(sender, [receiver], msg.as_string())
server.quit()
