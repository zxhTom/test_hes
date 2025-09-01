import sys
from pytest_check import check as original_check


class _TerminatingCheck:
    """
    如果启用 terminate_on_fail，assert 失败时会终止程序
    """

    def __init__(self, terminate_on_fail=False):
        self.terminate_on_fail = terminate_on_fail

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is AssertionError and self.terminate_on_fail:
            print(f"Assertion failed, terminating: {exc_val}", file=sys.stderr)
            sys.exit(1)
        # 否则，交给原始 check 处理（继续执行）
        return original_check.__exit__(exc_type, exc_val, exc_tb)


# 默认行为：不终止（兼容原版 check）
check = original_check
check = _TerminatingCheck(terminate_on_fail=True)


def enable_terminate_on_fail():
    """启用 assert 失败时终止程序"""
    global check
    check = _TerminatingCheck(terminate_on_fail=True)


def disable_terminate_on_fail():
    """恢复默认行为（assert 失败继续执行）"""
    global check
    check = original_check
