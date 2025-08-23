import os
from typing import List


class EmailConfig:
    """Email Configuration"""

    SENDER = os.getenv("TEST_REPORT_SENDER", "zxhtom13141@163.com")
    RECEIVERS = os.getenv(
        "TEST_REPORT_RECEIVERS", "zxhtom1314@163.com,870775401@qq.com"
    ).split(",")
    PASSWORD = os.getenv("TEST_REPORT_PASSWORD", "MKvK43eH7C8dP4qu")
    SMTP_SERVER = os.getenv("TEST_REPORT_SMTP_SERVER", "smtp.163.com")
    SMTP_PORT = int(os.getenv("TEST_REPORT_SMTP_PORT", "465"))


class ReportConfig:
    """报告生成配置"""

    ALLURE_RESULTS_DIR = "allure-results"
    ALLURE_REPORT_DIR = "allure-report"
    PDF_REPORT_PATH = "test_report.pdf"
    PDF_REPORT_NAME = "test_report.pdf"
    ALWAYS_SEND = os.getenv("TEST_REPORT_ALWAYS_SEND", "false").lower() == "true"
    ENABLED = os.getenv("TEST_REPORT_ENABLED", "false").lower() == "true"
