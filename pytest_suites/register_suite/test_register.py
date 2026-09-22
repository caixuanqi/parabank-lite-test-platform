# -*- coding: utf-8 -*-
"""注册模块测试套件 —— 17 条用例（REG_001 ~ REG_017）。

用例数据来自 testcase_spec.py，与《ParaBank Lite 业务规则与测试用例设计》
第四节用例表一致；提示文案与被测系统 parabank_lite.py 严格对齐。
"""
import os

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from browser_setup import (fail_with_screenshot, override_cases, save_screenshot,
                           wait_any_message)
from testcase_spec import cases_of

CASES = override_cases(cases_of('register'))
WAIT = int(os.environ.get('PB_WAIT', '8'))   # 等待元素的秒数，可用 PB_WAIT 调整
FIELDS = ('username', 'password', 'confirm')


def _message(driver, case, selector):
    """等元素出现；超时先留截图，再按原异常类型抛出（平台归因 TIMEOUT_）。"""
    try:
        el = WebDriverWait(driver, WAIT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
    except Exception as e:
        shot = save_screenshot(driver, case['code'])
        if shot and hasattr(e, 'msg'):
            e.msg = f'{e.msg}（失败截图：{shot}）'
        raise
    return el.text


@pytest.mark.parametrize('case', CASES, ids=[c['code'] for c in CASES])
def test_register(driver, base_url, case):
    """注册表单校验与注册主流程。"""
    driver.get(f'{base_url}/register')
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.NAME, 'username')))

    for field in FIELDS:
        el = driver.find_element(By.NAME, field)
        el.clear()
        el.send_keys(case['form'][field])
    driver.find_element(By.ID, 'btn-register').click()

    if case['success']:
        el = wait_any_message(driver, WAIT, case)
        msg = el.text
        if 'msg error' in (el.get_attribute('class') or ''):
            fail_with_screenshot(
                driver, case['code'],
                f"{case['code']} {case['title']}：预期注册成功，实际提示「{msg}」")
        if '注册成功' not in msg:
            fail_with_screenshot(driver, case['code'],
                                 f"{case['code']} 注册成功提示异常：「{msg}」")
        return

    msg = _message(driver, case, '.msg.error')
    if case['expect_msg'] != msg.strip():
        fail_with_screenshot(
            driver, case['code'],
            f"{case['code']} {case['title']}：预期提示「{case['expect_msg']}」，实际「{msg.strip()}」")
