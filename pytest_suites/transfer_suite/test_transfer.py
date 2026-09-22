# -*- coding: utf-8 -*-
"""转账模块测试套件 —— 16 条用例（TRAN_01 ~ TRAN_16）。

用例数据来自 testcase_spec.py，与《ParaBank Lite 业务规则与测试用例设计（最新版）》
及《转账模块测试用例.xlsx》一致；提示文案与被测系统 parabank_lite.py 严格对齐。
前置条件：以预置账号 admin_01 登录后进入转账页。
"""
import os

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from browser_setup import (fail_with_screenshot, override_cases, save_screenshot,
                           wait_any_message)
from testcase_spec import TRANSFER_USER, cases_of

CASES = override_cases(cases_of('transfer'))
WAIT = int(os.environ.get('PB_WAIT', '8'))   # 等待元素的秒数，可用 PB_WAIT 调整
TRANSFER_ACCOUNT, TRANSFER_PASSWORD = TRANSFER_USER


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


def _login(driver, base_url):
    driver.get(f'{base_url}/login')
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.NAME, 'username')))
    driver.find_element(By.NAME, 'username').send_keys(TRANSFER_ACCOUNT)
    driver.find_element(By.NAME, 'password').send_keys(TRANSFER_PASSWORD)
    driver.find_element(By.ID, 'btn-login').click()
    WebDriverWait(driver, WAIT).until(lambda d: '/accounts' in d.current_url)


@pytest.mark.parametrize('case', CASES, ids=[c['code'] for c in CASES])
def test_transfer(driver, base_url, case):
    """转账金额校验、账户校验与转账主流程。"""
    _login(driver, base_url)
    driver.get(f'{base_url}/transfer')
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, 'amount')))

    Select(driver.find_element(By.NAME, 'from_account')) \
        .select_by_value(case['form']['from_account'])
    to_account = driver.find_element(By.NAME, 'to_account')
    to_account.clear()
    to_account.send_keys(case['form']['to_account'])
    amount = driver.find_element(By.ID, 'amount')
    amount.clear()
    amount.send_keys(case['form']['amount'])
    driver.find_element(By.ID, 'btn-transfer').click()

    if case['success']:
        el = wait_any_message(driver, WAIT, case)
        msg = el.text
        if 'msg error' in (el.get_attribute('class') or ''):
            fail_with_screenshot(
                driver, case['code'],
                f"{case['code']} {case['title']}：预期转账成功，实际提示「{msg}」")
        if '转账成功' not in msg:
            fail_with_screenshot(driver, case['code'],
                                 f"{case['code']} 转账成功提示异常：「{msg}」")
        return

    msg = _message(driver, case, '.msg.error')
    if case['expect_msg'] != msg.strip():
        fail_with_screenshot(
            driver, case['code'],
            f"{case['code']} {case['title']}：预期提示「{case['expect_msg']}」，实际「{msg.strip()}」")
