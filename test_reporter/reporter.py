import os
import smtplib
import subprocess
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import Optional

from .config import EmailConfig, ReportConfig


class TestReporter:
    """测试报告生成与发送器"""

    def __init__(self):
        self.email_config = EmailConfig()
        self.report_config = ReportConfig()

    def generate_allure_report(self) -> bool:
        """生成Allure报告"""
        try:
            # 确保目录存在
            os.makedirs(self.report_config.ALLURE_RESULTS_DIR, exist_ok=True)
            os.makedirs(self.report_config.ALLURE_REPORT_DIR, exist_ok=True)

            # 生成Allure HTML报告
            subprocess.run(
                [
                    "allure",
                    "generate",
                    self.report_config.ALLURE_RESULTS_DIR,
                    "-o",
                    self.report_config.ALLURE_REPORT_DIR,
                    "--clean",
                    "--single-file",
                ],
                check=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"生成Allure报告失败: {e}")
            return False

    def convert_to_pdf(self) -> Optional[str]:
        """将Allure报告转换为PDF"""
        try:
            # 尝试使用allure命令行工具直接生成PDF
            subprocess.run(
                [
                    "allure",
                    "generate",
                    self.report_config.ALLURE_REPORT_DIR,
                    "-o",
                    self.report_config.PDF_REPORT_PATH,
                    "--format",
                    "pdf",
                ],
                check=True,
            )
            # os.makedirs(self.report_config.PDF_REPORT_PATH, exist_ok=True)
            # return os.path.join(
            #     self.report_config.PDF_REPORT_PATH, self.report_config.PDF_REPORT_NAME
            # )
            return self.report_config.PDF_REPORT_PATH
        except subprocess.CalledProcessError:
            try:
                # 回退方案: 使用wkhtmltopdf
                import pdfkit

                index_html = os.path.join(
                    self.report_config.ALLURE_REPORT_DIR, "index.html"
                )
                pdfkit.from_file(index_html, self.report_config.PDF_REPORT_PATH)
                return self.report_config.PDF_REPORT_PATH
            except Exception as e:
                print(f"生成PDF报告失败: {e}")
                return None

    def send_report_email(
        self, pdf_path: str, failed_count: int, total_count: int
    ) -> bool:
        """发送带PDF附件的测试报告邮件"""
        if not self.email_config.ENABLED:
            print("邮件通知功能已禁用")
            return False

        # 创建邮件
        msg = MIMEMultipart()
        msg["From"] = self.email_config.SENDER
        msg["To"] = ", ".join(self.email_config.RECEIVERS)

        # 设置邮件主题
        status = "失败" if failed_count > 0 else "成功"
        msg["Subject"] = f"[{status}] 自动化测试报告 - {failed_count}/{total_count}"

        # 邮件正文
        body = f"""
        <h2>自动化测试结果通知</h2>
        <p>测试状态: {status}</p>
        <p>测试用例总数: {total_count}</p>
        <p>失败用例数: {failed_count}</p>
        <p>报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>详细测试报告请查看附件PDF文件。</p>
        """
        msg.attach(MIMEText(body, "html"))
        # 添加PDF附件
        with open(pdf_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(pdf_path))
            part["Content-Disposition"] = (
                f'attachment; filename="{os.path.basename(pdf_path)}"'
            )
            msg.attach(part)

        # 发送邮件
        try:
            with smtplib.SMTP_SSL(
                self.email_config.SMTP_SERVER, self.email_config.SMTP_PORT
            ) as server:
                server.login(self.email_config.SENDER, self.email_config.PASSWORD)
                server.sendmail(
                    self.email_config.SENDER,
                    self.email_config.RECEIVERS,
                    msg.as_string(),
                )
            print("测试报告邮件已发送")
            return True
        except Exception as e:
            print(f"发送测试报告邮件时出错: {e}")
            return False

    def cleanup(self, pdf_path: str):
        """清理临时文件"""
        try:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
        except Exception as e:
            print(f"清理临时文件时出错: {e}")

    def generate_and_send_report(self, failed_count: int, total_count: int) -> bool:
        """生成报告并发送邮件"""
        if not self.email_config.ENABLED and not self.report_config.ALWAYS_SEND:
            print("邮件通知功能已禁用且未设置总是发送报告")
            return False

        # 生成Allure报告
        if not self.generate_allure_report():
            return False

        # 转换为PDF
        # pdf_path = self.convert_to_pdf()
        # if not pdf_path:
        #     return False
        pdf_path = "allure-report.pdf"

        # 发送邮件
        send_success = True
        if failed_count > 0 or self.report_config.ALWAYS_SEND:
            send_success = self.send_report_email(pdf_path, failed_count, total_count)

        # 清理临时文件
        self.cleanup(pdf_path)

        return send_success
