import random
from datetime import datetime, timedelta


def generate_random_time_range(
    start_date=None,
    end_date=None,
    min_duration_hours=1,
    max_duration_hours=24,
    business_hours_only=False,
):
    """
    生成随机时间范围

    参数:
    - start_date: 起始日期时间(默认当前时间)
    - end_date: 结束日期时间(默认当前时间+30天)
    - min_duration_hours: 最小持续时间(小时)
    - max_duration_hours: 最大持续时间(小时)
    - business_hours_only: 是否只生成工作时间(9:00-18:00)

    返回:
    - (start_time, end_time) 元组
    """

    # 设置默认时间范围
    now = datetime.now()
    if start_date is None:
        start_date = now
    if end_date is None:
        end_date = now + timedelta(days=30)

    # 确保时间范围有效
    if start_date >= end_date:
        raise ValueError("开始时间必须早于结束时间")

    # 计算总秒数范围
    total_seconds = int((end_date - start_date).total_seconds())

    # 生成随机开始时间
    random_seconds = random.randint(0, total_seconds)
    start_time = start_date + timedelta(seconds=random_seconds)

    # 生成随机持续时间(秒)
    duration_hours = random.uniform(min_duration_hours, max_duration_hours)
    duration = timedelta(hours=duration_hours)

    # 计算结束时间
    end_time = start_time + duration

    # 如果结束时间超出范围，则调整
    if end_time > end_date:
        end_time = end_date
        start_time = end_time - duration
        if start_time < start_date:
            start_time = start_date
            end_time = start_time + duration

    # 处理工作时间限制
    if business_hours_only:
        # 调整开始时间到工作时间
        if start_time.hour < 9:
            start_time = start_time.replace(hour=9, minute=0, second=0)
        elif start_time.hour >= 18:
            start_time = start_time.replace(hour=17, minute=0, second=0)
            start_time += timedelta(days=1)

        # 调整结束时间不超过18:00
        if end_time.hour >= 18:
            end_time = end_time.replace(hour=17, minute=59, second=59)

    return start_time, end_time


# 使用示例
if __name__ == "__main__":
    # 基本用法
    start, end = generate_random_time_range()
    print(
        f"随机时间范围: {start.strftime('%Y-%m-%d %H:%M')} - {end.strftime('%Y-%m-%d %H:%M')}"
    )

    # 指定日期范围
    custom_start = datetime(2023, 1, 1)
    custom_end = datetime(2023, 12, 31)
    start, end = generate_random_time_range(
        start_date=custom_start, end_date=custom_end
    )
    print(
        f"2023年内随机时间范围: {start.strftime('%m-%d %H:%M')} - {end.strftime('%m-%d %H:%M')}"
    )

    # 工作时间范围
    start, end = generate_random_time_range(business_hours_only=True)
    print(f"工作时间随机范围: {start.strftime('%a %H:%M')} - {end.strftime('%a %H:%M')}")

    # 短时间范围(1-4小时)
    start, end = generate_random_time_range(min_duration_hours=1, max_duration_hours=4)
    print(f"短时间范围: 持续时间 {round((end-start).total_seconds()/3600, 1)}小时")
