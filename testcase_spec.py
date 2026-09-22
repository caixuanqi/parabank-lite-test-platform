# -*- coding: utf-8 -*-
"""ParaBank Lite 业务规则与测试用例设计 —— 单一事实来源（spec）。

来源：《ParaBank Lite 业务规则与测试用例设计（最新版）.docx》
     《登录模块测试用例.xlsx》《注册模块测试用例.xlsx》《转账模块测试用例.xlsx》

被测系统（parabank_lite.py）、pytest 套件（pytest_suites/*）、
测试平台 seed（app.py）与文档（docs/测试用例设计.md）全部由本文件派生，
改这里即可全局同步，一致性由 check_consistency.py 校验。

用例字段说明：
    code         用例编号，如 LOGIN_001 / REG_001 / TRAN_01
    title        用例标题
    module       项目/模块，如 登录页
    suite        所属套件 key：login / register / transfer
    priority     P0 / P1 / P2
    category     功能 / 异常（有效等价类→功能，无效等价类→异常）
    precondition 前置条件
    steps        测试步骤（list）
    data         测试数据（展示用文案，与用例表一致）
    form         提交给被测系统的实际字段值
    expect       预期结果（展示用文案，与用例表一致）
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
        'description': '验证 ParaBank Lite 登录流程（13 条用例）',
        'test_file': 'test_login.py', 'test_func': 'test_login',
        'base_path': '/login',
    },
    {
        'key': 'register', 'suite_name': '注册模块测试', 'module': '注册',
        'path': 'register_suite', 'case_prefix': 'REG',
        'description': '验证 ParaBank Lite 注册流程（22 条用例）',
        'test_file': 'test_register.py', 'test_func': 'test_register',
        'base_path': '/register',
    },
    {
        'key': 'transfer', 'suite_name': '转账模块测试', 'module': '转账',
        'path': 'transfer_suite', 'case_prefix': 'TRAN',
        'description': '验证 ParaBank Lite 转账流程（16 条用例）',
        'test_file': 'test_transfer.py', 'test_func': 'test_transfer',
        'base_path': '/transfer',
    },
]

# ============================================================
# 二、业务规则（文档第二节原文 + 落地口径）
# ============================================================
RULES = [
    # ---- 登录 ----
    {'module': '登录', 'no': 1, 'text': '用户名必填，长度 6 ~ 20 位', 'deviation': ''},
    {'module': '登录', 'no': 2, 'text': '用户名只允许字母、数字、下划线', 'deviation': ''},
    {'module': '登录', 'no': 3, 'text': '密码必填，长度 6 ~ 20 位', 'deviation': ''},
    {'module': '登录', 'no': 4, 'text': '密码只允许字母、数字和字符 @ # $ . _', 'deviation': ''},
    {'module': '登录', 'no': 5, 'text': '用户名必须已在系统中注册', 'deviation': ''},
    {'module': '登录', 'no': 6, 'text': '密码必须与注册时一致', 'deviation': ''},
    {'module': '登录', 'no': 7, 'text': '用户名或密码任一为空时，不允许提交', 'deviation': ''},
    # ---- 注册 ----
    {'module': '注册', 'no': 1, 'text': '用户名必填，长度 6 ~ 20 位', 'deviation': ''},
    {'module': '注册', 'no': 2, 'text': '用户名只允许字母、数字、下划线', 'deviation': ''},
    {'module': '注册', 'no': 3, 'text': '用户名必须全局唯一，不能与已有账号重复',
     'deviation': 'REG_010 文档用 admin 触发，但 admin 只有 5 位、过不了 6~20 长度校验，'
                  '落地改用预置账号 admin_01（8 位，已注册）'},
    {'module': '注册', 'no': 4, 'text': '密码必填，长度 6 ~ 20 位',
     'deviation': 'REG_015 文档写"21位合法字符"，落地用 21 位合规密码 Pass12345678901234567'},
    {'module': '注册', 'no': 5, 'text': '密码必须同时包含字母和数字，且只允许字母、数字和字符 @ # $ . _',
     'deviation': ''},
    {'module': '注册', 'no': 6, 'text': '确认密码必须与密码保持一致', 'deviation': ''},
    # ---- 转账 ----
    {'module': '转账', 'no': 1, 'text': '转账金额必填', 'deviation': ''},
    {'module': '转账', 'no': 2, 'text': '金额范围 0.01 ~ 50000.00 元', 'deviation': ''},
    {'module': '转账', 'no': 3, 'text': '金额最多保留 2 位小数', 'deviation': ''},
    {'module': '转账', 'no': 4, 'text': '金额只能包含数字和一个小数点',
     'deviation': 'TRAN_07（-50）要求提示"金额必须大于 0"，故校验顺序为：字符集 → 小数点个数 '
                  '→ 格式 → 小数位 → 数值范围；负号放行到数值校验'},
    {'module': '转账', 'no': 5, 'text': '源账户余额必须 ≥ 转账金额',
     'deviation': '预置账户 10003 余额 100.00，供 TRAN_14（余额不足）使用'},
    {'module': '转账', 'no': 6, 'text': '源账户和目标账户不能相同', 'deviation': ''},
    {'module': '转账', 'no': 7, 'text': '目标账户必须存在', 'deviation': ''},
]

# 落地口径（文档本身需要澄清的地方）
DECISIONS = [
    {'item': '登录用户名长度', 'decision': '按最新版文档为 6~20 位（旧版文档为 3~20，已作废）'},
    {'item': '登录密码过短（LOGIN_011）',
     'decision': '文档数据 Admin1 是 6 位、无法触发"密码过短"，落地用 5 位 Admin'},
    {'item': '含汉字用例的用户名（LOGIN_009 / REG_008）',
     'decision': '文档给"管理员01""用户01"，都不足 6 位、会先触发长度校验，'
                 '落地补足位数（管理员001 / 用户0001）以命中字符集校验'},
    {'item': '注册用户名已存在（REG_010）',
     'decision': '文档数据 admin（5 位）过不了 6~20 长度校验，落地改用预置账号 admin_01'},
    {'item': '注册用户名含空格（REG_009）', 'decision': '文档未填优先级，按同类格式错误用例定为 P2'},
    {'item': '转账用例编号', 'decision': '文档为 TRAN_01~TRAN_16（两位），登录/注册为三位，'
                                        '落地保持文档原编号不变'},
    {'item': '文案中的排版空格',
     'decision': '文档"金额必须大于 0""单笔金额不能超过 50000 元""金额最多保留 2 位小数"'
                 '中的空格为排版空格，落地时去掉'},
    {'item': '同一规则在两模块的文案差异',
     'decision': '登录表写"用户名只能含字母、数字、下划线""密码只允许字母、数字和字符@#$._"，'
                 '注册表写"用户名只能包含字母、数字和下划线""密码只能包含字母、数字和@#$._"，'
                 '落地按各模块表分别实现'},
    {'item': '核心模块"账户查询"', 'decision': '文档未给规则与用例，本期未覆盖'},
    {'item': '初始账号 admin/admin123', 'decision': '保留；另按登录等价类补预置测试主账号 '
                                                   'admin_01/Admin@123（持有账户 10001/10002/10003）'
                                                   '与 user_2026/Pass123'},
    {'item': '是否需要"用户被锁定"规则', 'decision': '暂不加'},
    {'item': '登录是否区分"账号不存在"与"密码错误"',
     'decision': '区分（LOGIN_002/003 分开，提示文案分别实现）'},
]

# ============================================================
# 三、等价类划分
# ============================================================
EQUIVALENCE = {
    '登录': [
        ('用户名', '长度', '6~20 位', 'admin_01、user_2026', '<6 或 >20 位', 'ab、a×21'),
        ('用户名', '字符类型', '字母/数字/下划线', 'user_01、admin_01', '含其他字符',
         'user@01、用户01、user 01'),
        ('用户名', '空值', '非空', 'admin_01', '空', '（空）'),
        ('用户名', '存在性', '已注册', 'admin_01', '未注册', 'nobody_999'),
        ('密码', '长度', '6~20 位', 'admin123', '<6 或 >20 位', 'admin1、a×21'),
        ('密码', '字符类型', '字母/数字/@#$._', 'admin@123、pass_$123', '含其他字符',
         'admin&123、admin 123、admin中文123'),
        ('密码', '空值', '非空', 'admin@123', '空', '（空）'),
        ('密码', '一致性', '与注册时一致', 'admin@123', '不一致', 'Wrong@123'),
    ],
    '注册': [
        ('用户名', '长度', '6~20 位', 'alice01、user_2026', '小于 6 位或大于 20 位',
         'n123、21 位用户名'),
        ('用户名', '字符类型', '字母、数字、下划线', 'alice_01、user2026', '含其他字符',
         'alice@、用户01、alice 01'),
        ('用户名', '空值', '非空', 'alice01', '为空', '（空）'),
        ('用户名', '唯一性', '未注册', 'alice_2026', '已存在', 'admin_01'),
        ('密码', '长度', '6~20 位', 'Pass123、Ab1234', '小于 6 位或大于 20 位', 'Pa123、21 位密码'),
        ('密码', '组成', '同时包含字母和数字', 'Pass123、abc123', '纯字母或纯数字', 'abcdef、123456'),
        ('密码', '字符类型', '字母、数字、@#$._', 'Pass@123、Abc_123', '含其他特殊字符、中文、空格',
         'Pass%123、Pass中123、Pass 123'),
        ('密码', '空值', '非空', 'Pass123', '为空', '（空）'),
        ('确认密码', '一致性', '与密码完全一致', 'Pass123 / Pass123', '与密码不一致',
         'Pass123 / Pass124'),
    ],
    '转账': [
        ('转账金额', '范围', '0.01 ~ 50000.00', '100、0.01、50000.00', '≤0 或 >50000',
         '0、-50、50000.01'),
        ('转账金额', '小数位', '最多 2 位', '100、100.5、100.50', '≥3 位', '0.123、100.999'),
        ('转账金额', '字符类型', '仅数字 + 小数点', '100.5', '含其他字符（字母、汉字、逗号）',
         '100a、一百、1,000'),
        ('转账金额', '小数点个数', '≤1 个', '100、100.50', '≥2 个小数点', '1.2.3、1..2'),
        ('转账金额', '空值', '非空', '100', '为空', '（空）'),
        ('转账金额', '格式校验', '合法数字格式', '0.01、100.50', '仅输入小数点', '.、.123'),
        ('余额', '余额充足性', '余额 ≥ 转账金额', '余额 1000，转 100', '余额 < 转账金额',
         '余额 100，转 200'),
        ('源/目标账户', '账户差异', '源、目标账户不同', 'A→B', '源账户 = 目标账户', 'A→A'),
        ('目标账户', '账户存在性', '目标账户已存在', '10002', '目标账户不存在', '99999'),
    ],
}

# ============================================================
# 四、预置演示数据（被测系统初始化，套件执行前会重置）
# ============================================================
# admin_01：登录模块的合规账号（文档等价类指定），同时是转账主账号
# admin：文档"初始账号"，保留但不再持有账户
# user_2026：登录/注册等价类中列出的有效数据
PRESET_USERS = [
    {'username': 'admin_01', 'password': 'Admin@123',
     'accounts': [('10001', 100000.00), ('10002', 0.00), ('10003', 100.00)]},
    {'username': 'admin', 'password': 'admin123', 'accounts': []},
    {'username': 'user_2026', 'password': 'Pass123', 'accounts': [('20002', 0.00)]},
]

# 转账用例使用的账户
ACC_MAIN = '10001'        # 余额充足：100000.00
ACC_TARGET = '10002'      # 转入账户：0.00
ACC_LOW = '10003'         # 余额不足专用：100.00
ACC_NOT_EXIST = '99999'

# 转账套件/手工验证台登录用的账号（持有上述账户）
TRANSFER_USER = ('admin_01', 'Admin@123')

_LOGIN_DEFAULTS = {'username': 'admin_01', 'password': 'Admin@123'}
_REG_DEFAULTS = {'password': 'Pass123', 'confirm': 'Pass123'}
_LONG_NAME = 'a' * 21
_LONG_PWD = 'Pass12345678901234567'      # 21 位：合规字符，超长


def _login(code, title, priority, category, username, password,
           expect_msg, expect, data,
           steps=('1. 输入用户名', '2. 输入密码', '3. 点击登录'),
           precondition='打开登录页'):
    return {
        'code': code, 'title': title, 'module': '登录页', 'suite': 'login',
        'priority': priority, 'category': category,
        'precondition': precondition, 'steps': list(steps), 'data': data,
        'form': {'username': username, 'password': password},
        'expect': expect, 'expect_msg': expect_msg,
        'success': expect_msg is None,
        'pytest_node_suffix': f'[{code}]',
    }


def _reg(code, title, priority, category, username=None, password=None,
         confirm=None, expect_msg=None, expect='', data='',
         steps=('1. 输入用户名', '2. 输入密码', '3. 输入相同确认密码', '4. 点击注册'),
         precondition='打开注册页'):
    form = {
        'username': username if username is not None else 'alice01',
        'password': password if password is not None else _REG_DEFAULTS['password'],
        'confirm': confirm if confirm is not None else (
            password if password is not None else _REG_DEFAULTS['confirm']),
    }
    return {
        'code': code, 'title': title, 'module': '注册页', 'suite': 'register',
        'priority': priority, 'category': category,
        'precondition': precondition, 'steps': list(steps), 'data': data,
        'form': form, 'expect': expect, 'expect_msg': expect_msg,
        'success': expect_msg is None,
        'pytest_node_suffix': f'[{code}]',
    }


def _tran(code, title, priority, category, amount, expect_msg,
          expect='', data='', from_acc=ACC_MAIN, to_acc=ACC_TARGET,
          steps=('1. 输入金额', '2. 选择目标账户', '3. 提交')):
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
# 五、测试用例表（51 条：登录 13 + 注册 22 + 转账 16）
# ============================================================
CASES = [
    # ---------------- 登录模块（13 条） ----------------
    _login('LOGIN_001', '合法登录', 'P0', '功能', 'admin_01', 'Admin@123', None,
           '合法，跳转账户概览', '用户名：admin_01 / 密码：Admin@123',
           precondition='打开登录页，系统已预置合规账号'),
    _login('LOGIN_002', '密码错误', 'P0', '异常', 'admin_01', 'Wrong@123', '密码错误',
           '不合法，提示"密码错误"', '用户名：admin_01 / 密码：Wrong@123',
           steps=('1. 输入已注册用户名', '2. 输入错误密码', '3. 点击登录'),
           precondition='打开登录页，系统已预置合规账号'),
    _login('LOGIN_003', '账号不存在', 'P0', '异常', 'nobody_999', 'Admin@123', '账号不存在',
           '不合法，提示"账号不存在"', '用户名：nobody_999 / 密码：Admin@123',
           steps=('1. 输入未注册用户名', '2. 输入任意合规密码', '3. 点击登录')),
    _login('LOGIN_004', '用户名为空', 'P1', '异常', '', 'Admin@123', '用户名必填',
           '不合法，提示"用户名必填"，无法提交', '用户名：（空）/ 密码：Admin@123',
           steps=('1. 用户名留空', '2. 输入合规密码', '3. 点击登录')),
    _login('LOGIN_005', '密码为空', 'P1', '异常', 'admin_01', '', '密码必填',
           '不合法，提示"密码必填"', '用户名：admin_01 / 密码：（空）',
           steps=('1. 输入合规用户名', '2. 密码留空', '3. 点击登录')),
    _login('LOGIN_006', '用户名过短', 'P1', '异常', 'admin', 'Admin@123', '用户名长度6-20位',
           '不合法，提示"用户名长度6-20位"', '用户名：admin / 密码：Admin@123',
           steps=('1. 输入 5 位用户名', '2. 输入合规密码', '3. 点击登录')),
    _login('LOGIN_007', '用户名过长', 'P2', '异常', 'admin_01234567890123456789', 'Admin@123',
           '用户名长度6-20位', '不合法，提示"用户名长度6-20位"',
           '用户名：admin_01234567890123456789 / 密码：Admin@123',
           steps=('1. 输入 21 位用户名', '2. 输入合规密码', '3. 点击登录')),
    _login('LOGIN_008', '用户名含特殊字符', 'P2', '异常', 'admin@01', 'Admin@123',
           '用户名只能含字母、数字、下划线', '不合法，提示"用户名只能含字母、数字、下划线"',
           '用户名：admin@01 / 密码：Admin@123',
           steps=('1. 输入含非法特殊字符的用户名', '2. 输入合规密码', '3. 点击登录')),
    _login('LOGIN_009', '用户名含汉字', 'P2', '异常', '管理员001', 'Admin@123',
           '用户名只能含字母、数字、下划线', '不合法，提示"用户名只能含字母、数字、下划线"',
           '用户名：管理员01 / 密码：Admin@123',
           steps=('1. 输入含汉字的用户名', '2. 输入合规密码', '3. 点击登录')),
    _login('LOGIN_010', '用户名含空格', 'P2', '异常', 'admin 01', 'Admin@123',
           '用户名只能含字母、数字、下划线', '不合法，提示"用户名只能含字母、数字、下划线"',
           '用户名：admin 01 / 密码：Admin@123',
           steps=('1. 输入含空格的用户名', '2. 输入合规密码', '3. 点击登录')),
    _login('LOGIN_011', '密码过短', 'P2', '异常', 'admin_01', 'Admin', '密码长度6-20位',
           '不合法，提示"密码长度6-20位"', '用户名：admin_01 / 密码：Admin',
           steps=('1. 输入合规用户名', '2. 输入 5 位密码', '3. 点击登录')),
    _login('LOGIN_012', '密码超长', 'P2', '异常', 'admin_01', _LONG_PWD, '密码长度6-20位',
           '不合法，提示"密码长度6-20位"', '用户名：admin_01 / 密码：21 位合法字符',
           steps=('1. 输入合规用户名', '2. 输入 21 位密码', '3. 点击登录')),
    _login('LOGIN_013', '密码含非法特殊字符', 'P2', '异常', 'admin_01', 'Admin&123',
           '密码只允许字母、数字和字符@#$._',
           '不合法，提示"密码只允许字母、数字和字符@#$._"',
           '用户名：admin_01 / 密码：Admin&123',
           steps=('1. 输入合规用户名', '2. 输入含非法字符的密码', '3. 点击登录')),

    # ---------------- 注册模块（22 条） ----------------
    _reg('REG_001', '合法注册', 'P0', '功能', username='alice01',
         data='用户名：alice01 / 密码：Pass123 / 确认密码：Pass123',
         expect='合法，注册成功'),
    _reg('REG_002', '用户名为空', 'P1', '异常', username='', expect_msg='用户名必填',
         data='用户名：（空）/ 密码：Pass123 / 确认密码：Pass123',
         expect='不合法，提示"用户名必填"',
         steps=('1. 用户名留空', '2. 输入密码', '3. 输入相同确认密码', '4. 点击注册')),
    _reg('REG_003', '用户名过短', 'P1', '异常', username='alice', expect_msg='用户名长度6-20位',
         data='用户名：alice / 密码：Pass123 / 确认密码：Pass123',
         expect='不合法，提示"用户名长度6-20位"',
         steps=('1. 输入 5 位用户名', '2. 输入密码', '3. 输入相同确认密码', '4. 点击注册')),
    _reg('REG_004', '用户名最小边界', 'P0', '功能', username='alice1',
         data='用户名：alice1 / 密码：Pass123 / 确认密码：Pass123',
         expect='合法，注册成功',
         steps=('1. 输入 6 位用户名', '2. 输入密码', '3. 输入相同确认密码', '4. 点击注册')),
    _reg('REG_005', '用户名最大边界', 'P0', '功能', username='abcdefghijklmnopqrst',
         data='用户名：abcdefghijklmnopqrst / 密码：Pass123 / 确认密码：Pass123',
         expect='合法，注册成功',
         steps=('1. 输入 20 位用户名', '2. 输入密码', '3. 输入相同确认密码', '4. 点击注册')),
    _reg('REG_006', '用户名超长', 'P1', '异常', username=_LONG_NAME,
         expect_msg='用户名长度6-20位',
         data='用户名：21 位字符 / 密码：Pass123 / 确认密码：Pass123',
         expect='不合法，提示"用户名长度6-20位"',
         steps=('1. 输入 21 位用户名', '2. 输入密码', '3. 输入相同确认密码', '4. 点击注册')),
    _reg('REG_007', '用户名含特殊字符', 'P1', '异常', username='alice@1',
         expect_msg='用户名只能包含字母、数字和下划线',
         data='用户名：alice@1 / 密码：Pass123 / 确认密码：Pass123',
         expect='不合法，提示"用户名只能包含字母、数字和下划线"',
         steps=('1. 输入含特殊字符的用户名', '2. 输入密码', '3. 输入相同确认密码', '4. 点击注册')),
    _reg('REG_008', '用户名含中文', 'P1', '异常', username='用户0001',
         expect_msg='用户名只能包含字母、数字和下划线',
         data='用户名：用户01 / 密码：Pass123 / 确认密码：Pass123',
         expect='不合法，提示用户名格式错误',
         steps=('1. 输入含中文的用户名', '2. 输入密码', '3. 输入相同确认密码', '4. 点击注册')),
    _reg('REG_009', '用户名含空格', 'P2', '异常', username='alice 01',
         expect_msg='用户名只能包含字母、数字和下划线',
         data='用户名：alice 01 / 密码：Pass123 / 确认密码：Pass123',
         expect='不合法，提示用户名格式错误',
         steps=('1. 输入含空格的用户名', '2. 输入密码', '3. 输入相同确认密码', '4. 点击注册')),
    _reg('REG_010', '用户名已存在', 'P0', '异常', username='admin_01',
         expect_msg='用户名已存在',
         data='用户名：admin_01 / 密码：Pass123 / 确认密码：Pass123',
         expect='不合法，提示"用户名已存在"',
         steps=('1. 输入已有用户名', '2. 输入合法密码', '3. 输入相同确认密码', '4. 点击注册'),
         precondition='系统中已存在 admin_01 账号'),
    _reg('REG_011', '密码为空', 'P1', '异常', password='', confirm='', expect_msg='密码必填',
         data='用户名：alice01 / 密码：（空）/ 确认密码：（空）',
         expect='不合法，提示"密码必填"',
         steps=('1. 输入合法用户名', '2. 密码留空', '3. 输入相同确认密码', '4. 点击注册')),
    _reg('REG_012', '密码过短', 'P1', '异常', password='Pass1', expect_msg='密码长度6-20位',
         data='用户名：alice01 / 密码：Pass1 / 确认密码：Pass1',
         expect='不合法，提示"密码长度6-20位"',
         steps=('1. 输入合法用户名', '2. 输入 5 位密码', '3. 输入相同确认密码', '4. 点击注册')),
    _reg('REG_013', '密码最小边界', 'P0', '功能', password='Pass12',
         data='用户名：alice01 / 密码：Pass12 / 确认密码：Pass12',
         expect='合法，注册成功',
         steps=('1. 输入合法用户名', '2. 输入 6 位密码', '3. 输入相同确认密码', '4. 点击注册')),
    _reg('REG_014', '密码最大边界', 'P0', '功能', password='Pass123456789012345',
         data='用户名：alice01 / 密码：20 位合法字符 / 确认密码：20 位合法字符',
         expect='合法，注册成功',
         steps=('1. 输入合法用户名', '2. 输入 20 位密码', '3. 输入相同确认密码', '4. 点击注册')),
    _reg('REG_015', '密码超长', 'P1', '异常', password=_LONG_PWD, expect_msg='密码长度6-20位',
         data='用户名：alice01 / 密码：21 位合法字符 / 确认密码：21 位合法字符',
         expect='不合法，提示"密码长度6-20位"',
         steps=('1. 输入合法用户名', '2. 输入 21 位密码', '3. 输入相同确认密码', '4. 点击注册')),
    _reg('REG_016', '密码纯字母', 'P1', '异常', password='abcdef',
         expect_msg='密码必须包含字母和数字',
         data='用户名：alice01 / 密码：abcdef / 确认密码：abcdef',
         expect='不合法，提示"密码必须包含字母和数字"',
         steps=('1. 输入合法用户名', '2. 输入纯字母密码', '3. 输入相同确认密码', '4. 点击注册')),
    _reg('REG_017', '密码纯数字', 'P1', '异常', password='123456',
         expect_msg='密码必须包含字母和数字',
         data='用户名：alice01 / 密码：123456 / 确认密码：123456',
         expect='不合法，提示"密码必须包含字母和数字"',
         steps=('1. 输入合法用户名', '2. 输入纯数字密码', '3. 输入相同确认密码', '4. 点击注册')),
    _reg('REG_018', '密码包含合法特殊字符', 'P0', '功能', password='Pass@#$._123',
         data='用户名：alice01 / 密码：Pass@#$._123 / 确认密码：Pass@#$._123',
         expect='合法，注册成功',
         steps=('1. 输入合法用户名', '2. 输入包含允许特殊字符的密码',
                '3. 输入相同确认密码', '4. 点击注册')),
    _reg('REG_019', '密码含非法特殊字符', 'P1', '异常', password='Pass%123',
         expect_msg='密码只能包含字母、数字和@#$._',
         data='用户名：alice01 / 密码：Pass%123 / 确认密码：Pass%123',
         expect='不合法，提示"密码只能包含字母、数字和@#$._"',
         steps=('1. 输入合法用户名', '2. 输入包含非法特殊字符的密码',
                '3. 输入相同确认密码', '4. 点击注册')),
    _reg('REG_020', '密码含中文', 'P1', '异常', password='Pass中123',
         expect_msg='密码只能包含字母、数字和@#$._',
         data='用户名：alice01 / 密码：Pass中123 / 确认密码：Pass中123',
         expect='不合法，提示密码格式错误',
         steps=('1. 输入合法用户名', '2. 输入包含中文的密码', '3. 输入相同确认密码', '4. 点击注册')),
    _reg('REG_021', '密码含空格', 'P1', '异常', password='Pass 123',
         expect_msg='密码只能包含字母、数字和@#$._',
         data='用户名：alice01 / 密码：Pass 123 / 确认密码：Pass 123',
         expect='不合法，提示密码格式错误',
         steps=('1. 输入合法用户名', '2. 输入包含空格的密码', '3. 输入相同确认密码', '4. 点击注册')),
    _reg('REG_022', '两次密码不一致', 'P0', '异常', password='Pass123', confirm='Pass124',
         expect_msg='两次密码不一致',
         data='用户名：alice01 / 密码：Pass123 / 确认密码：Pass124',
         expect='不合法，提示"两次密码不一致"',
         steps=('1. 输入合法用户名', '2. 输入密码', '3. 输入不同的确认密码', '4. 点击注册')),

    # ---------------- 转账模块（16 条） ----------------
    _tran('TRAN_01', '合法整数金额', 'P0', '功能', '100', None,
          '合法，转账成功', '金额 100'),
    _tran('TRAN_02', '合法 1 位小数', 'P0', '功能', '100.5', None,
          '合法，转账成功', '金额 100.5'),
    _tran('TRAN_03', '合法 2 位小数', 'P0', '功能', '100.50', None,
          '合法，转账成功', '金额 100.50'),
    _tran('TRAN_04', '最小金额边界', 'P0', '功能', '0.01', None,
          '合法，转账成功', '金额 0.01'),
    _tran('TRAN_05', '最大金额边界', 'P0', '功能', '50000.00', None,
          '合法，转账成功', '金额 50000.00'),
    _tran('TRAN_06', '金额为 0', 'P1', '异常', '0', '金额必须大于0',
          '不合法，提示"金额必须大于0"', '金额 0'),
    _tran('TRAN_07', '金额为负数', 'P1', '异常', '-50', '金额必须大于0',
          '不合法，提示"金额必须大于0"', '金额 -50'),
    _tran('TRAN_08', '金额超上限', 'P1', '异常', '50000.01', '单笔金额不能超过50000元',
          '不合法，提示"单笔金额不能超过50000元"', '金额 50000.01'),
    _tran('TRAN_09', '金额 3 位小数', 'P1', '异常', '100.999', '金额最多保留2位小数',
          '不合法，提示"金额最多保留2位小数"', '金额 100.999'),
    _tran('TRAN_10', '金额含任意字符', 'P1', '异常', '100a', '只能输入数字和小数点',
          '不合法，提示"只能输入数字和小数点"', '金额 100a'),
    _tran('TRAN_11', '多个小数点', 'P1', '异常', '1.2.3', '仅允许一个小数点',
          '不合法，提示"仅允许一个小数点"', '金额 1.2.3'),
    _tran('TRAN_12', '仅输入小数点', 'P2', '异常', '.', '请输入有效金额',
          '不合法，提示"请输入有效金额"', '金额 .'),
    _tran('TRAN_13', '金额为空', 'P1', '异常', '', '转账金额不能为空',
          '不合法，提示"转账金额不能为空"', '（空）',
          steps=('1. 金额留空', '2. 选择目标账户', '3. 提交')),
    _tran('TRAN_14', '余额不足', 'P0', '异常', '200', '账户余额不足',
          '不合法，提示"账户余额不足"', '余额 100 / 转 200', from_acc=ACC_LOW),
    _tran('TRAN_15', '源账户与目标账户相同', 'P1', '异常', '100', '源账户和目标账户不能相同',
          '不合法，提示"源账户和目标账户不能相同"', 'A→A', to_acc=ACC_MAIN,
          steps=('1. 选择目标账户为自己账户', '2. 提交')),
    _tran('TRAN_16', '目标账户不存在', 'P2', '异常', '100', '目标账户不存在',
          '不合法，提示"目标账户不存在"', '目标账号 99999', to_acc=ACC_NOT_EXIST,
          steps=('1. 输入不存在的目标账号', '2. 提交')),
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
    """汇总统计（按用例表实际统计）"""
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
# 用例表严格按最新版文档与三张 xlsx，数据与预期结果未作改动（除第二节记录的
# 落地口径外）；失败来自被测系统侧注入的缺陷。
# 缺陷实现在 parabank_lite.py 中以 BUG-01 ~ BUG-03 标记，统一开关
# parabank_lite.INJECT_DEFECTS；置为 False 即恢复"完全符合文档"的系统，
# 51 条应当全绿。
# ============================================================
INJECTED_DEFECTS = [
    {
        'id': 'BUG-01',
        'title': '登录未区分"账号不存在"与"密码错误"',
        'rule': '2.1(5) 用户名必须已在系统中注册 / 2.1(6) 密码必须与注册时一致',
        'desc': '两种情况统一提示"用户名或密码错误"，与用例表要求的"账号不存在""密码错误"不符。',
        'layer': 'route', 'expect_prefix': 'ASSERT_',
        'cases': ['LOGIN_002', 'LOGIN_003'],
    },
    {
        'id': 'BUG-02',
        'title': '转账金额上限边界判断错误',
        'rule': '2.3(2) 金额范围 0.01 ~ 50000.00 元',
        'desc': '边界判断写成"≥ 50000 即超限"，恰好 50000.00 被误判为超过上限。',
        'layer': 'validator', 'expect_prefix': 'ASSERT_',
        'cases': ['TRAN_05'],
    },
    {
        'id': 'BUG-03',
        'title': '漏做"仅允许一个小数点"校验',
        'rule': '2.3(4) 金额只能包含数字和一个小数点',
        'desc': '去掉了小数点个数校验，1.2.3 这类输入落到小数位校验上，'
                '提示变成"金额最多保留2位小数"。',
        'layer': 'validator', 'expect_prefix': 'ASSERT_',
        'cases': ['TRAN_11'],
    },
]


def expected_failures():
    """预期失败的用例 {用例编号: 缺陷编号}。"""
    return {code: d['id'] for d in INJECTED_DEFECTS for code in d['cases']}


def defect_of(case_code):
    return next((d for d in INJECTED_DEFECTS if case_code in d['cases']), None)
