# -*- coding: utf-8 -*-
"""ParaBank Lite 业务规则与测试用例设计 —— 单一事实来源（spec）。

来源：《ParaBank Lite 业务规则与测试用例设计.docx》

被测系统（parabank_lite.py）、pytest 套件（pytest_suites/*）、
测试平台 seed（app.py）与文档（docs/测试用例设计.md）全部由本文件派生，
改这里即可全局同步，一致性由 check_consistency.py 校验。

用例字段说明：
    code         用例编号，如 LOGIN_001
    title        用例标题
    module       项目/模块，如 登录页
    suite        所属套件 key：login / register / transfer
    priority     P0 / P1 / P2
    category     功能 / 异常（有效等价类→功能，无效等价类→异常）
    precondition 前置条件
    steps        测试步骤（list）
    data         测试数据（展示用文案，与文档一致）
    form         提交给被测系统的实际字段值
    expect       预期结果（展示用文案，与文档一致）
    expect_msg   期望提示文案，None 表示预期成功
    success      True 表示该用例预期成功
"""

# ============================================================
# 一、套件定义（与测试平台 test_suites 一一对应）
# ============================================================
MODULES = [
    {
        'key': 'login', 'suite_name': '登录模块测试', 'module': '登录',
        'path': 'login_suite', 'case_prefix': 'LOGIN',
        'description': '验证 ParaBank Lite 登录流程（10 条用例）',
        'test_file': 'test_login.py', 'test_func': 'test_login',
        'base_path': '/login',
    },
    {
        'key': 'register', 'suite_name': '注册模块测试', 'module': '注册',
        'path': 'register_suite', 'case_prefix': 'REG',
        'description': '验证 ParaBank Lite 注册流程（17 条用例）',
        'test_file': 'test_register.py', 'test_func': 'test_register',
        'base_path': '/register',
    },
    {
        'key': 'transfer', 'suite_name': '转账模块测试', 'module': '转账',
        'path': 'transfer_suite', 'case_prefix': 'TRAN',
        'description': '验证 ParaBank Lite 转账流程（18 条用例）',
        'test_file': 'test_transfer.py', 'test_func': 'test_transfer',
        'base_path': '/transfer',
    },
]

# ============================================================
# 二、业务规则（文档第二节原文 + 落地口径）
# ============================================================
RULES = [
    # ---- 登录 ----
    {'module': '登录', 'no': 1, 'text': '用户名必填，长度 3 ~ 20 位',
     'deviation': '文档原文写 6~20 位，但等价类表（3~20 位）、用例 LOGIN_006/007 '
                  '（提示"用户名长度3-20位"）与预置账号 admin（5 位）均为 3~20，按 3~20 落地'},
    {'module': '登录', 'no': 2, 'text': '用户名只允许字母、数字、下划线', 'deviation': ''},
    {'module': '登录', 'no': 3, 'text': '密码必填，长度 6 ~ 20 位', 'deviation': ''},
    {'module': '登录', 'no': 4, 'text': '密码只允许字母、数字和字符 @ # $ . _',
     'deviation': '文档未给该规则的等价类与用例，本期在系统中实现但无用例覆盖'},
    {'module': '登录', 'no': 5, 'text': '用户名必须已在系统中注册', 'deviation': ''},
    {'module': '登录', 'no': 6, 'text': '密码必须与注册时一致', 'deviation': ''},
    {'module': '登录', 'no': 7, 'text': '用户名或密码任一为空时，不允许提交', 'deviation': ''},
    # ---- 注册 ----
    {'module': '注册', 'no': 1, 'text': '用户名必填，长度 6 ~ 20 位', 'deviation': ''},
    {'module': '注册', 'no': 2, 'text': '用户名只允许字母、数字、下划线', 'deviation': ''},
    {'module': '注册', 'no': 3, 'text': '用户名必须全局唯一，不能与已有账号重复',
     'deviation': '预置账号 admin 仅 5 位，过不了 6~20 长度校验，无法触发"用户名已存在"；'
                  '因此预置第二个合规账号 user_2026（6~20 位）供 REG_002 使用'},
    {'module': '注册', 'no': 4, 'text': '密码必填，长度 6 ~ 20 位', 'deviation': ''},
    {'module': '注册', 'no': 5, 'text': '密码必须同时包含字母和数字，且只允许字母、数字和字符 @ # $ . _',
     'deviation': '文档未给字符集部分的等价类与用例，本期实现但无用例覆盖'},
    {'module': '注册', 'no': 6, 'text': '两次密码必须一致', 'deviation': ''},
    {'module': '注册', 'no': 7, 'text': '任一项为空时，不允许提交',
     'deviation': '按用户要求，本期不做手机号与邮箱功能：文档 2.2(7) 手机号、2.2(8) 邮箱'
                  '两条规则及对应用例（REG_012~REG_017）移出本期范围，注册规则数 9 → 7'},
    # ---- 转账 ----
    {'module': '转账', 'no': 1, 'text': '转账金额必填', 'deviation': ''},
    {'module': '转账', 'no': 2, 'text': '金额范围 0.01 ~ 50000.00 元', 'deviation': ''},
    {'module': '转账', 'no': 3, 'text': '金额最多 2 位小数', 'deviation': ''},
    {'module': '转账', 'no': 4, 'text': '金额只能包含数字和一个小数点',
     'deviation': 'TRAN_007（-50）要求提示"金额必须大于0"，故校验顺序为：字符集 → 小数点个数 '
                  '→ 格式 → 小数位 → 数值范围；负号放行到数值校验'},
    {'module': '转账', 'no': 5, 'text': '源账户余额必须 ≥ 转账金额',
     'deviation': '预置账户 10003 余额 100.00，供 TRAN_016（余额不足）使用'},
    {'module': '转账', 'no': 6, 'text': '源账户和目标账户不能相同', 'deviation': ''},
    {'module': '转账', 'no': 7, 'text': '目标账户必须存在', 'deviation': ''},
]

# 文档第六节待确认事项的落地口径
DECISIONS = [
    {'item': '登录模块规则（7 条）', 'decision': '保留（用户名长度按 3~20 落地）'},
    {'item': '注册模块规则（9 条）',
     'decision': '保留 7 条：手机号、邮箱两条规则本期不做，连同 REG_012~REG_017 移出范围'},
    {'item': '注册手机号、邮箱功能',
     'decision': '本期不添加（用户决定），注册表单只保留用户名 / 密码 / 确认密码'},
    {'item': '转账模块规则（7 条）', 'decision': '保留'},
    {'item': '初始账号 admin/admin123', 'decision': '保留，并补充预置账号 user_2026/Pass123 与账户 10003'},
    {'item': '是否需要"用户被锁定"规则', 'decision': '暂不加'},
    {'item': '登录是否区分"账号不存在"与"密码错误"', 'decision': '方案 1：区分（LOGIN_002/003 均保留）'},
]

# ============================================================
# 三、等价类划分
# ============================================================
EQUIVALENCE = {
    '登录': [
        ('用户名', '长度', '3~20 位', 'admin、user_01', '<3 或 >20 位', 'ab、a×21'),
        ('用户名', '字符类型', '字母/数字/下划线', 'user_01', '含其他字符', 'user@01、用户01、user 01'),
        ('用户名', '空值', '非空', 'admin', '空', '（空）'),
        ('用户名', '存在性', '已注册', 'admin', '未注册', 'nobody999'),
        ('密码', '长度', '6~20 位', 'admin123', '<6 或 >20 位', '12345、a×21'),
        ('密码', '空值', '非空', 'admin123', '空', '（空）'),
        ('密码', '一致性', '与注册时一致', 'admin123', '不一致', 'wrongpwd'),
    ],
    '注册': [
        ('用户名', '长度', '6~20 位', 'alice01、user_2026', '<6 或 >20 位', 'n123、a×21'),
        ('用户名', '字符类型', '字母/数字/下划线', 'alice_01', '含其他字符', 'alice@、爱丽丝、alice 01'),
        ('用户名', '唯一性', '未注册', 'alice_20260920', '已存在', 'user_2026'),
        ('用户名', '空值', '非空', 'alice01', '空', '（空）'),
        ('密码', '长度', '6~20 位', 'Pass123', '<6 或 >20 位', '12345、a×21'),
        ('密码', '组成', '字母+数字', 'Pass123', '纯字母或纯数字', 'abcdef、123456'),
        ('密码', '空值', '非空', 'Pass123', '空', '（空）'),
        ('确认密码', '一致性', '与密码相同', 'Pass123/Pass123', '与密码不同', 'Pass123/Pass999'),
    ],
    '转账': [
        ('转账金额', '范围', '0.01 ~ 50000.00', '100、0.01、50000.00', '≤0 或 >50000', '0、-50、50000.01'),
        ('转账金额', '小数位', '最多 2 位', '100、100.5、100.50', '≥3 位', '0.123、100.999'),
        ('转账金额', '字符类型', '数字+小数点', '100.50', '含其他字符', '100a、一百、1,000'),
        ('转账金额', '小数点个数', '≤1', '100、100.50', '≥2', '1.2.3、1..2'),
        ('转账金额', '空值', '非空', '100', '空', '（空）'),
        ('转账金额', '格式', '有效格式', '0.01、100.50', '只有小数点', '.、.123'),
        ('余额', '充足性', '余额 ≥ 金额', '1000余额转100', '余额 < 金额', '100余额转200'),
        ('源/目标账户', '差异', '不同账户', 'A→B', '相同账户', 'A→A'),
        ('目标账户', '存在性', '已存在', '10002', '不存在', '99999'),
    ],
}

# ============================================================
# 四、预置演示数据（被测系统初始化，套件执行前会重置）
# ============================================================
PRESET_USERS = [
    {'username': 'admin', 'password': 'admin123',
     'accounts': [('10001', 100000.00), ('10002', 0.00), ('10003', 100.00)]},
    {'username': 'user_2026', 'password': 'Pass123',
     'accounts': [('20002', 0.00)]},
]

# 转账用例使用的账户
ACC_MAIN = '10001'        # 余额充足：100000.00
ACC_TARGET = '10002'      # 转入账户：0.00
ACC_LOW = '10003'         # 余额不足专用：100.00
ACC_NOT_EXIST = '99999'

_REG_DEFAULTS = {'password': 'Pass123', 'confirm': 'Pass123'}
_LONG_NAME = 'a' * 21


def _login(code, title, priority, category, username, password,
           expect_msg, expect, data, steps=('1. 输入用户名 2. 输入密码 3. 点击登录',)):
    return {
        'code': code, 'title': title, 'module': '登录页', 'suite': 'login',
        'priority': priority, 'category': category,
        'precondition': '打开登录页', 'steps': list(steps), 'data': data,
        'form': {'username': username, 'password': password},
        'expect': expect, 'expect_msg': expect_msg,
        'success': expect_msg is None,
        'pytest_node_suffix': f'[{code}]',
    }


def _reg(code, title, priority, category, username=None, password=None,
         confirm=None, expect_msg=None, expect='',
         data='', steps=('1. 填写完整信息 2. 点击注册',)):
    form = {
        'username': username if username is not None else 'alice01',
        'password': password if password is not None else _REG_DEFAULTS['password'],
        'confirm': confirm if confirm is not None else (
            password if password is not None else _REG_DEFAULTS['confirm']),
    }
    return {
        'code': code, 'title': title, 'module': '注册页', 'suite': 'register',
        'priority': priority, 'category': category,
        'precondition': '打开注册页', 'steps': list(steps), 'data': data,
        'form': form, 'expect': expect, 'expect_msg': expect_msg,
        'success': expect_msg is None,
        'pytest_node_suffix': f'[{code}]',
    }


def _tran(code, title, priority, category, amount, expect_msg,
          expect='', data='', from_acc=ACC_MAIN, to_acc=ACC_TARGET,
          steps=('1. 输入金额 2. 选择目标账户 3. 提交',)):
    return {
        'code': code, 'title': title, 'module': '转账页', 'suite': 'transfer',
        'priority': priority, 'category': category,
        'precondition': '登录后进入转账页', 'steps': list(steps), 'data': data,
        'form': {'from_account': from_acc, 'to_account': to_acc, 'amount': amount},
        'expect': expect, 'expect_msg': expect_msg,
        'success': expect_msg is None,
        'pytest_node_suffix': f'[{code}]',
    }


# ============================================================
# 五、测试用例表（39 条：登录 10 + 注册 11 + 转账 18）
# ============================================================
CASES = [
    # ---------------- 4.1 登录模块（10 条） ----------------
    _login('LOGIN_001', '合法登录', 'P0', '功能', 'admin', 'admin123', None,
           '合法，跳转账户概览', 'admin / admin123'),
    _login('LOGIN_002', '密码错误', 'P0', '异常', 'admin', 'wrongpwd', '密码错误',
           '不合法，提示"密码错误"', 'admin / wrongpwd'),
    _login('LOGIN_003', '账号不存在', 'P0', '异常', 'nobody999', 'admin123', '账号不存在',
           '不合法，提示"账号不存在"', 'nobody999 / admin123'),
    _login('LOGIN_004', '用户名为空', 'P1', '异常', '', 'admin123', '用户名必填',
           '不合法，提示"用户名必填"', '（空） / admin123',
           steps=('1. 用户名留空 2. 输入密码 3. 点击登录',)),
    _login('LOGIN_005', '密码为空', 'P1', '异常', 'admin', '', '密码必填',
           '不合法，提示"密码必填"', 'admin / （空）',
           steps=('1. 输入用户名 2. 密码留空 3. 点击登录',)),
    _login('LOGIN_006', '用户名过短', 'P1', '异常', 'ab', 'admin123', '用户名长度3-20位',
           '不合法，提示"用户名长度3-20位"', 'ab / admin123',
           steps=('1. 输入 2 位用户名 2. 输入密码 3. 点击登录',)),
    _login('LOGIN_007', '用户名超长', 'P2', '异常', _LONG_NAME, 'admin123', '用户名长度3-20位',
           '不合法，提示"用户名长度3-20位"', 'a×21 / admin123',
           steps=('1. 输入 21 位用户名 2. 输入密码 3. 点击登录',)),
    _login('LOGIN_008', '用户名含特殊字符', 'P1', '异常', 'user@01', 'admin123',
           '用户名只能含字母数字下划线', '不合法，提示"用户名只能含字母数字下划线"',
           'user@01 / admin123',
           steps=('1. 输入含 @ 的用户名 2. 输入密码 3. 点击登录',)),
    _login('LOGIN_009', '用户名含汉字', 'P2', '异常', '用户01', 'admin123',
           '用户名只能含字母数字下划线', '不合法，提示格式错误', '用户01 / admin123',
           steps=('1. 输入汉字用户名 2. 输入密码 3. 点击登录',)),
    _login('LOGIN_010', '密码过短', 'P1', '异常', 'admin', '12345', '密码长度6-20位',
           '不合法，提示"密码长度6-20位"', 'admin / 12345',
           steps=('1. 输入用户名 2. 输入 5 位密码 3. 点击登录',)),

    # ---------------- 4.2 注册模块（11 条） ----------------
    _reg('REG_001', '合法注册', 'P0', '功能', username='alice_20260920',
         data='alice_20260920 / Pass123 / Pass123',
         expect='合法，注册成功跳转登录'),
    _reg('REG_002', '用户名已存在', 'P0', '异常', username='user_2026',
         expect_msg='用户名已存在', data='user_2026 / Pass123 / Pass123',
         expect='不合法，提示"用户名已存在"',
         steps=('1. 用户名填 user_2026 2. 其他填齐 3. 点击注册',)),
    _reg('REG_003', '用户名过短', 'P0', '异常', username='n123', expect_msg='用户名长度6-20位',
         data='n123 / Pass123 / Pass123', expect='不合法，提示"用户名长度6-20位"',
         steps=('1. 用户名填 n123 2. 其他填齐 3. 点击注册',)),
    _reg('REG_004', '用户名超长', 'P1', '异常', username=_LONG_NAME, expect_msg='用户名长度6-20位',
         data='a×21 / Pass123 / Pass123', expect='不合法，提示"用户名长度6-20位"',
         steps=('1. 用户名填 21 位 2. 其他填齐 3. 点击注册',)),
    _reg('REG_005', '用户名为空', 'P1', '异常', username='', expect_msg='用户名必填',
         data='（空）/ Pass123 / Pass123', expect='不合法，提示"用户名必填"',
         steps=('1. 用户名留空 2. 其他填齐 3. 点击注册',)),
    _reg('REG_006', '用户名含特殊字符', 'P1', '异常', username='alice@',
         expect_msg='用户名只能含字母数字下划线', data='alice@ / Pass123 / Pass123',
         expect='不合法，提示格式错误',
         steps=('1. 用户名填 alice@ 2. 其他填齐 3. 点击注册',)),
    _reg('REG_007', '密码过短', 'P1', '异常', password='12345', expect_msg='密码长度6-20位',
         data='alice01 / 12345 / 12345', expect='不合法，提示"密码长度6-20位"',
         steps=('1. 密码填 12345 2. 其他填齐 3. 点击注册',)),
    _reg('REG_008', '密码纯数字', 'P1', '异常', password='123456', expect_msg='密码必须含字母和数字',
         data='alice01 / 123456 / 123456', expect='不合法，提示"密码必须含字母和数字"',
         steps=('1. 密码填 123456 2. 其他填齐 3. 点击注册',)),
    _reg('REG_009', '密码纯字母', 'P1', '异常', password='abcdef', expect_msg='密码必须含字母和数字',
         data='alice01 / abcdef / abcdef', expect='不合法，提示"密码必须含字母和数字"',
         steps=('1. 密码填 abcdef 2. 其他填齐 3. 点击注册',)),
    _reg('REG_010', '两次密码不一致', 'P0', '异常', password='Pass123', confirm='Pass999',
         expect_msg='两次密码不一致', data='alice01 / Pass123 / Pass999',
         expect='不合法，提示"两次密码不一致"',
         steps=('1. 密码 Pass123 2. 确认密码 Pass999 3. 点击注册',)),
    _reg('REG_011', '密码为空', 'P1', '异常', password='', confirm='',
         expect_msg='密码必填', data='alice01 / （空）/ （空）', expect='不合法，提示"密码必填"',
         steps=('1. 密码留空 2. 其他填齐 3. 点击注册',)),
    # ---------------- 4.3 转账模块（18 条） ----------------
    _tran('TRAN_001', '合法整数金额', 'P0', '功能', '100', None,
          '合法，转账成功', '金额 100'),
    _tran('TRAN_002', '合法 1 位小数', 'P0', '功能', '100.5', None,
          '合法，转账成功', '金额 100.5', steps=('1. 输入金额 2. 提交',)),
    _tran('TRAN_003', '合法 2 位小数', 'P0', '功能', '100.50', None,
          '合法，转账成功', '金额 100.50', steps=('1. 输入金额 2. 提交',)),
    _tran('TRAN_004', '最小金额边界', 'P0', '功能', '0.01', None,
          '合法，转账成功', '金额 0.01', steps=('1. 输入金额 2. 提交',)),
    _tran('TRAN_005', '最大金额边界', 'P0', '功能', '50000.00', None,
          '合法，转账成功', '金额 50000.00', steps=('1. 输入金额 2. 提交',)),
    _tran('TRAN_006', '金额为 0', 'P1', '异常', '0', '金额必须大于0',
          '不合法，提示"金额必须大于0"', '金额 0', steps=('1. 输入金额 2. 提交',)),
    _tran('TRAN_007', '金额为负数', 'P1', '异常', '-50', '金额必须大于0',
          '不合法，提示"金额必须大于0"', '金额 -50', steps=('1. 输入金额 2. 提交',)),
    _tran('TRAN_008', '金额超上限', 'P1', '异常', '50000.01', '单笔不超过50000元',
          '不合法，提示"单笔不超过50000"', '金额 50000.01', steps=('1. 输入金额 2. 提交',)),
    _tran('TRAN_009', '金额 3 位小数', 'P1', '异常', '100.999', '金额最多2位小数',
          '不合法，提示"最多2位小数"', '金额 100.999', steps=('1. 输入金额 2. 提交',)),
    _tran('TRAN_010', '金额含字母', 'P1', '异常', '100a', '金额只能输入数字和小数点',
          '不合法，提示"只能输入数字和小数点"', '金额 100a', steps=('1. 输入金额 2. 提交',)),
    _tran('TRAN_011', '金额含汉字', 'P1', '异常', '一百', '金额只能输入数字和小数点',
          '不合法，提示"只能输入数字和小数点"', '金额 一百', steps=('1. 输入金额 2. 提交',)),
    _tran('TRAN_012', '金额含逗号', 'P2', '异常', '1,000', '金额只能输入数字和小数点',
          '不合法，提示"只能输入数字和小数点"', '金额 1,000', steps=('1. 输入金额 2. 提交',)),
    _tran('TRAN_013', '多个小数点', 'P1', '异常', '1.2.3', '小数点最多1个',
          '不合法，提示"小数点最多1个"', '金额 1.2.3', steps=('1. 输入金额 2. 提交',)),
    _tran('TRAN_014', '只有小数点', 'P2', '异常', '.', '请输入有效金额',
          '不合法，提示"请输入有效金额"', '金额 .', steps=('1. 输入金额 2. 提交',)),
    _tran('TRAN_015', '金额为空', 'P1', '异常', '', '金额不能为空',
          '不合法，提示"金额不能为空"', '（空）', steps=('1. 金额留空 2. 提交',)),
    _tran('TRAN_016', '余额不足', 'P0', '异常', '200', '余额不足',
          '不合法，提示"余额不足"', '余额 100 / 转 200',
          from_acc=ACC_LOW, steps=('1. 输入超过余额的金额 2. 提交',)),
    _tran('TRAN_017', '源目标账户相同', 'P1', '异常', '100', '账户不能相同',
          '不合法，提示"账户不能相同"', 'A→A',
          to_acc=ACC_MAIN, steps=('1. 目标账户选源账户 2. 提交',)),
    _tran('TRAN_018', '目标账户不存在', 'P2', '异常', '100', '目标账户不存在',
          '不合法，提示"账户不存在"', '目标 99999',
          to_acc=ACC_NOT_EXIST, steps=('1. 输入不存在的目标账户 2. 提交',)),
]


# ============================================================
# 六、派生工具函数
# ============================================================
def cases_of(suite_key):
    return [c for c in CASES if c['suite'] == suite_key]


def module_of(suite_key):
    return next(m for m in MODULES if m['key'] == suite_key)


def pytest_node(case):
    mod = module_of(case['suite'])
    return f"{mod['test_file']}::{mod['test_func']}{case['pytest_node_suffix']}"


def summary():
    """汇总统计（按用例表实际统计，覆盖文档第五节的口径）"""
    rows = []
    for m in MODULES:
        cs = cases_of(m['key'])
        rows.append({
            'module': m['module'],
            'rules': len([r for r in RULES if r['module'] == m['module']]),
            'equivalent': len(EQUIVALENCE[m['module']]),
            'cases': len(cs),
            'P0': len([c for c in cs if c['priority'] == 'P0']),
            'P1': len([c for c in cs if c['priority'] == 'P1']),
            'P2': len([c for c in cs if c['priority'] == 'P2']),
        })
    total = {
        'module': '合计',
        'rules': sum(r['rules'] for r in rows),
        'equivalent': sum(r['equivalent'] for r in rows),
        'cases': sum(r['cases'] for r in rows),
        'P0': sum(r['P0'] for r in rows),
        'P1': sum(r['P1'] for r in rows),
        'P2': sum(r['P2'] for r in rows),
    }
    return rows, total


# ============================================================
# 七、注入缺陷登记表（演示用）
# ------------------------------------------------------------
# 用例表严格照《ParaBank Lite 业务规则与测试用例设计.docx》第四节，
# 45 条的数据与预期结果一个字未改；失败来自被测系统侧注入的缺陷。
#
# 缺陷实现在 parabank_lite.py 中以 BUG-01 ~ BUG-06 标记，统一开关
# parabank_lite.INJECT_DEFECTS；置为 False 即恢复"完全符合文档"的
# 系统，45 条应当全绿。
#
# layer：缺陷所在层级
#   validator —— 校验层，check_consistency.py 能直接复现偏差
#   route     —— 路由/模板层，校验层正常，偏差体现在页面反馈上
# ============================================================
INJECTED_DEFECTS = [
    {
        'id': 'BUG-01',
        'title': '登录未区分"账号不存在"与"密码错误"',
        'rule': '2.1(5) 用户名必须已在系统中注册 / 2.1(6) 密码必须与注册时一致',
        'desc': '文档第六节选择"方案 1：区分"，此处刻意按"方案 2"实现，'
                '两种情况统一提示"用户名或密码错误"。',
        'layer': 'route', 'expect_prefix': 'ASSERT_',
        'cases': ['LOGIN_002', 'LOGIN_003'],
    },
    {
        'id': 'BUG-02',
        'title': '转账金额上限边界判断错误',
        'rule': '2.3(2) 金额范围 0.01 ~ 50000.00 元',
        'desc': '边界判断写成"≥ 50000 即超限"，恰好 50000.00 被误判为超过上限。',
        'layer': 'validator', 'expect_prefix': 'ASSERT_',
        'cases': ['TRAN_005'],
    },
    {
        'id': 'BUG-04',
        'title': '注册成功后不显示成功提示',
        'rule': '用例 REG_001 预期"合法，注册成功跳转登录"',
        'desc': '账号实际已创建，但页面不渲染 .msg.success 提示，'
                '自动化用例等待成功提示超时。',
        'layer': 'route', 'expect_prefix': 'TIMEOUT_',
        'cases': ['REG_001'],
    },
    {
        'id': 'BUG-05',
        'title': '转账成功后不显示成功提示',
        'rule': '用例 TRAN_001 ~ TRAN_005 预期"合法，转账成功"',
        'desc': '款项实际已划转，但页面不渲染 .msg.success 提示。'
                'TRAN_005 因 BUG-02 更早失败（金额上限），故此表只登记 TRAN_001~004。',
        'layer': 'route', 'expect_prefix': 'TIMEOUT_',
        'cases': ['TRAN_001', 'TRAN_002', 'TRAN_003', 'TRAN_004'],
    },
    {
        'id': 'BUG-06',
        'title': '漏做"小数点最多 1 个"校验',
        'rule': '2.3(4) 金额只能包含数字和一个小数点',
        'desc': '去掉了小数点个数校验，1.2.3 这类输入落到小数位校验上，'
                '提示变成"金额最多2位小数"。',
        'layer': 'validator', 'expect_prefix': 'ASSERT_',
        'cases': ['TRAN_013'],
    },
]


def expected_failures():
    """预期失败的用例 {用例编号: 缺陷编号}。"""
    return {code: d['id'] for d in INJECTED_DEFECTS for code in d['cases']}


def defect_of(case_code):
    return next((d for d in INJECTED_DEFECTS if case_code in d['cases']), None)
