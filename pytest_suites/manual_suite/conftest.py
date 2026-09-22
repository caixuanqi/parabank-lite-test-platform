import sys
from pathlib import Path

import pytest

# 项目根目录入 sys.path，共用 browser_setup.py
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from browser_setup import BASE_URL, create_driver  # noqa: E402


@pytest.fixture(scope='session')
def driver():
    """手工验证台用：一次执行共用一个浏览器。

    注意：手工验证不重置演示数据，保留你自己造出来的状态
    （账号、余额、流水都按实际情况来）。
    """
    d = create_driver()
    yield d
    try:
        d.quit()
    except Exception:
        pass


@pytest.fixture
def base_url():
    return BASE_URL
