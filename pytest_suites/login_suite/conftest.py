import sys
from pathlib import Path

import pytest

# 项目根目录入 sys.path：共用 browser_setup.py / testcase_spec.py
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from browser_setup import BASE_URL, SCREENSHOT_DIR, create_driver  # noqa: E402
from parabank_lite import reset_demo_data  # noqa: E402


@pytest.fixture(scope='session', autouse=True)
def demo_data():
    """套件执行前置：重置预置演示数据（余额/账号等前置条件可重复）。"""
    reset_demo_data()
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
