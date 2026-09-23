import sys
from pathlib import Path

import pytest

# 项目根目录入 sys.path：共用 browser_setup.py / testcase_spec.py
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from browser_setup import BASE_URL, SCREENSHOT_DIR, create_driver  # noqa: E402
from parabank_lite import delete_user, reset_demo_data  # noqa: E402


@pytest.fixture(scope='session', autouse=True)
def demo_data():
    """套件执行前置：重置预置演示数据。"""
    reset_demo_data()
    yield


@pytest.fixture(autouse=True)
def demo_data_per_case(request):
    """注册用例会创建账号，且用例表里多条"注册成功"用例复用同一用户名
    （REG_013 / REG_014 / REG_018 都用 user_01，REG_001 用 alice01）。

    因此每条用例前：重置演示数据 + 删掉本条用例要注册的用户名，
    保证"用户名未注册"这一隐含前置条件成立；
    前置条件写明"系统中已存在 XXX 账号"的用例（REG_010）则保留该账号。
    """
    reset_demo_data()
    callspec = getattr(request.node, 'callspec', None)
    if callspec:
        case = callspec.params.get('case') or {}
        if not case.get('precondition_user_exists'):
            delete_user(case.get('form', {}).get('username'))
    yield


@pytest.fixture(scope='session')
def driver():
    """整个套件共用一个浏览器实例（逐个用例新开浏览器太慢）。"""
    d = create_driver()
    yield d
    try:
        d.quit()
    except Exception:
        pass


@pytest.fixture(autouse=True)
def fresh_session(driver):
    """每个用例开始前清掉 cookie，避免用例之间互相影响。"""
    try:
        driver.delete_all_cookies()
    except Exception:
        pass
    yield


@pytest.fixture
def base_url():
    return BASE_URL


@pytest.fixture
def screenshot_dir():
    return SCREENSHOT_DIR
