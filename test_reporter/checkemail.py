import smtplib
import sys
import ssl
from email.mime.text import MIMEText

# 你的 163 邮箱账号和授权码
EMAIL = "zxhtom13141@163.com"
PASSWORD = "MKvK43eH7C8dP4qu"
TO = "870775401@qq.com"


# 测试邮件内容
msg = MIMEText("SMTP 诊断邮件", "plain", "utf-8")
msg["Subject"] = "SMTP 诊断"
msg["From"] = EMAIL
msg["To"] = TO


def check_tls_versions():
    print("\n=== 支持的 TLS 版本检测 ===")
    ctx = ssl.create_default_context()
    versions = []
    for proto in ["TLSv1", "TLSv1_1", "TLSv1_2", "TLSv1_3"]:
        try:
            ctx = ssl.SSLContext(getattr(ssl, f"PROTOCOL_{proto.replace('.', '_')}"))
            versions.append(proto)
        except Exception:
            pass
    print("本机 Python 支持的 TLS 协议:", versions)


def test_ssl_465():
    print("\n=== 测试 465 (SSL) ===")
    try:
        context = ssl.create_default_context()
        context.set_ciphers("HIGH:!aNULL:!eNULL")

        server = smtplib.SMTP_SSL("smtp.163.com", 465, context=context, timeout=10)
        server.set_debuglevel(1)  # 打印交互日志
        server.local_hostname = "127.0.0.1"
        server.login(EMAIL, PASSWORD)
        server.sendmail(EMAIL, [TO], msg.as_string())
        server.quit()
        print("✅ 465 SSL 发送成功")
    except Exception as e:
        print("❌ 465 SSL 失败:", e)


def test_starttls_587():
    print("\n=== 测试 587 (STARTTLS) ===")
    try:
        context = ssl.create_default_context()

        server = smtplib.SMTP("smtp.163.com", 587, timeout=10)
        server.set_debuglevel(1)
        server.local_hostname = "127.0.1.1"
        server.ehlo()
        server.starttls(context=context)
        server.login(EMAIL, PASSWORD)
        server.sendmail(EMAIL, [TO], msg.as_string())
        server.quit()
        print("✅ 587 STARTTLS 发送成功")
    except Exception as e:
        print("❌ 587 STARTTLS 失败:", e)


if __name__ == "__main__":
    print("Python 版本:", sys.version)
    check_tls_versions()
    test_ssl_465()
    test_starttls_587()
