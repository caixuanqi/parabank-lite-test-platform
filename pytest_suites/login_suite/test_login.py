# -*- coding: utf-8 -*-
"""登录模块测试套件 —— 10 条用例（LOGIN_001 ~ LOGIN_010）。

用例数据来自 testcase_spec.py，与《ParaBank Lite 业务规则与测试用例设计》
第四节用例表一致；提示文案与被测系统 parabank_lite.py 严格对齐。
"""
import os

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from browser_setup import fail_with_screenshot, override_cases, save_screenshot
from testcase_spec import cases_of

CASES = override_cases(cases_of('login'))
WAIT = int(os.environ.get('PB_WAIT', '8'))   # 等待元素的秒数，可用 PB_WAIT 调整


def _error_message(driver, case):
    """等错误提示出现；超时先留截图，再按原异常类型抛出（平台归因 TIMEOUT_）。"""
    try:
        el = WebDriverWait(driver, WAIT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.msg.error')))
    except Exception as e:
        shot = save_screenshot(driver, case['code'])
        if shot and hasattr(e, 'msg'):
            e.msg = f'{e.msg}（失败截图：{shot}）'
        raise
    return el.text


@pytest.mark.parametrize('case', CASES, ids=[c['code'] for c in CASES])
def test_login(driver, base_url, case):
    """用户名/密码校验与登录主流程。"""
    driver.get(f'{base_url}/login')
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.NAME, 'username')))

    username = driver.find_element(By.NAME, 'username')
    password = driver.find_element(By.NAME, 'password')
    username.clear()
    username.send_keys(case['form']['username'])
    password.clear()
    password.send_keys(case['form']['password'])
    driver.find_element(By.ID, 'btn-login').click()

    if case['success']:
        # 等"跳转到账户概览"或"出现错误提示"，哪个先到算哪个（避免白等满超时）
        try:
            WebDriverWait(driver, WAIT).until(
                lambda d: '/accounts' in d.current_url
                or d.find_elements(By.CSS_SELECTOR, '.msg.error'))
        except Exception as e:
            shot = save_screenshot(driver, case['code'])
            if shot and hasattr(e, 'msg'):
                e.msg = f'{e.msg}（失败截图：{shot}）'
            raise
        errors = driver.find_elements(By.CSS_SELECTOR, '.msg.error')
        if errors:
            fail_with_screenshot(
                driver, case['code'],
                f"{case['code']} {case['title']}：预期登录成功，实际提示「{errors[0].text}」")
        if not driver.find_elements(By.ID, 'accountTable'):
            fail_with_screenshot(driver, case['code'],
                                 f"{case['code']} 登录后未进入账户概览页")
        return

    msg = _error_message(driver, case)
    if case['expect_msg'] != msg.strip():
        fail_with_screenshot(
            driver, case['code'],
            f"{case['code']} {case['title']}：预期提示「{case['expect_msg']}」，实际「{msg.strip()}」")
