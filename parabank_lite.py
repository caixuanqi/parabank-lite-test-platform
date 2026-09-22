# -*- coding: utf-8 -*-
"""ParaBank Lite — 被测银行系统 (Flask Blueprint)"""
import os
import re
import sqlite3
from flask import (Blueprint, render_template, request,
                   redirect, url_for, session)
from werkzeug.security import generate_password_hash, check_password_hash

pb_bp = Blueprint('parabank', __name__,
                  template_folder='templates/parabank')

# 项目根目录 = 本文件所在目录（Windows / Linux 通用）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'parabank_test.db')

USERNAME_RE = re.compile(r'^[A-Za-z0-9_]+$')
PASSWORD_RE = re.compile(r'^[A-Za-z0-9@#$_\.]+$')
AMOUNT_RE = re.compile(r'^-?[\d.]*$')

# ============================================================
# 注入缺陷（演示用）：BUG-01 ~ BUG-03。
# 登记表见 testcase_spec.INJECTED_DEFECTS，每个缺陷都注明它违反文档的哪条
# 规则、预期让哪几条用例失败。置为 False 即恢复"完全符合文档"的系统，
# 51 条用例应当全绿。
# ============================================================
INJECT_DEFECTS = True

# 提示文案与校验顺序严格对齐《ParaBank Lite 业务规则与测试用例设计（最新版）》
# 与三张模块用例表的"预期结果"列，pytest 套件按同一文案断言。


def validate_login(username, password):
    if not username:
        return False, '用户名必填'
    if not (6 <= len(username) <= 20):
        return False, '用户名长度6-20位'
    if not USERNAME_RE.match(username):
        return False, '用户名只能含字母、数字、下划线'
    if not password:
        return False, '密码必填'
    if not (6 <= len(password) <= 20):
        return False, '密码长度6-20位'
    if not PASSWORD_RE.match(password):
        return False, '密码只允许字母、数字和字符@#$._'
    return True, None


def validate_register(username, password, confirm):
    if not username:
        return False, '用户名必填'
    if not (6 <= len(username) <= 20):
        return False, '用户名长度6-20位'
    if not USERNAME_RE.match(username):
        return False, '用户名只能包含字母、数字和下划线'
    if not password:
        return False, '密码必填'
    if not (6 <= len(password) <= 20):
        return False, '密码长度6-20位'
    if not PASSWORD_RE.match(password):
        return False, '密码只能包含字母、数字和@#$._'
    if not (re.search(r'[A-Za-z]', password) and re.search(r'\d', password)):
        return False, '密码必须包含字母和数字'
    if password != confirm:
        return False, '两次密码不一致'
    return True, None


def validate_transfer(amount_str, from_acc, to_acc):
    if not amount_str or not amount_str.strip():
        return False, None, '转账金额不能为空'
    s = amount_str.strip()
    if not AMOUNT_RE.match(s):
        return False, None, '只能输入数字和小数点'
    # BUG-03：漏做"仅允许一个小数点"校验（违反规则 2.3(4)，
    #         预期 TRAN_11 的提示变成"金额最多保留2位小数"）
    if s.count('.') > 1 and not INJECT_DEFECTS:
        return False, None, '仅允许一个小数点'
    body = s[1:] if s.startswith('-') else s
    if body in ('', '.') or body.startswith('.'):
        return False, None, '请输入有效金额'
    if '.' in body and len(body.split('.', 1)[1]) > 2:
        return False, None, '金额最多保留2位小数'
    try:
        amount = float(s)
    except ValueError:
        return False, None, '请输入有效金额'
    if amount <= 0:
        return False, None, '金额必须大于0'
    # BUG-02：上限边界判断写成"≥ 50000 即超限"（违反规则 2.3(2)，
    #         预期边界值 50000.00 的 TRAN_05 失败）
    if amount > 50000 or (INJECT_DEFECTS and amount == 50000):
        return False, None, '单笔金额不能超过50000元'
    if from_acc and to_acc and from_acc == to_acc:
        return False, None, '源账户和目标账户不能相同'
    return True, amount, None


def get_db():
    # timeout：平台与测试进程同时读写同一个库时等待锁
    conn = sqlite3.connect(DB_PATH, timeout=15)
    conn.row_factory = sqlite3.Row
    return conn


# 预置演示数据（与 testcase_spec.PRESET_USERS 保持一致，check_consistency.py 会校验）
# admin_01：登录模块的合规账号（等价类指定），同时持有转账用账户
#           10001 余额充足 / 10002 转入 / 10003 余额不足专用
# admin：文档"初始账号"，保留但不再持有账户
# user_2026：登录/注册等价类中列出的有效数据
PRESET_USERS = [
    {'username': 'admin_01', 'password': 'Admin@123',
     'accounts': [('10001', 100000.00), ('10002', 0.00), ('10003', 100.00)]},
    {'username': 'admin', 'password': 'admin123', 'accounts': []},
    {'username': 'user_2026', 'password': 'Pass123',
     'accounts': [('20002', 0.00)]},
]

DEMO_NOT_EXIST_ACCOUNT = '99999'


def _ensure_tables():
    conn = get_db()
    c = conn.cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS pb_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS pb_accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        account_number TEXT UNIQUE NOT NULL,
        balance REAL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS pb_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_account TEXT,
        to_account TEXT,
        amount REAL,
        txn_type TEXT,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()


def reset_demo_data():
    """恢复预置演示数据：预置账号与余额复位，清空测试新增的账号与交易流水。

    套件执行前调用（conftest.py 的 autouse fixture），保证用例前置条件可重复：
    - 10001 余额 100000.00（TRAN_005 需 ≥ 50000）
    - 10003 余额 100.00（TRAN_016 余额不足）
    - 目标账户 10002 存在，99999 不存在
    - user_2026 已注册（REG_002"用户名已存在"）
    """
    _ensure_tables()
    conn = get_db()
    c = conn.cursor()

    names = [u['username'] for u in PRESET_USERS]
    marks = ','.join('?' * len(names))
    c.execute(f'DELETE FROM pb_accounts WHERE user_id NOT IN '
              f'(SELECT id FROM pb_users WHERE username IN ({marks}))', names)
    c.execute(f'DELETE FROM pb_users WHERE username NOT IN ({marks})', names)

    for user in PRESET_USERS:
        row = c.execute('SELECT id FROM pb_users WHERE username=?',
                        (user['username'],)).fetchone()
        if row:
            uid = row['id']
            c.execute('UPDATE pb_users SET password_hash=? WHERE id=?',
                      (generate_password_hash(user['password']), uid))
        else:
            c.execute('INSERT INTO pb_users (username, password_hash) VALUES (?, ?)',
                      (user['username'], generate_password_hash(user['password'])))
            uid = c.lastrowid

        for acc_no, balance in user['accounts']:
            exists = c.execute('SELECT id FROM pb_accounts WHERE account_number=?',
                               (acc_no,)).fetchone()
            if exists:
                c.execute('UPDATE pb_accounts SET user_id=?, balance=? '
                          'WHERE account_number=?', (uid, balance, acc_no))
            else:
                c.execute('INSERT INTO pb_accounts (user_id, account_number, balance) '
                          'VALUES (?, ?, ?)', (uid, acc_no, balance))

    c.execute('DELETE FROM pb_transactions')
    conn.commit()
    conn.close()


def init_parabank_tables():
    """应用启动时调用：建表 + 预置演示数据。"""
    reset_demo_data()
    print('[pb] 预置演示数据就绪: ' +
          ', '.join(f"{u['username']}/{u['password']}" for u in PRESET_USERS))


@pb_bp.route('/')
def index():
    if 'pb_user' not in session:
        return redirect(url_for('parabank.login'))
    return redirect(url_for('parabank.accounts'))


@pb_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        password = request.form.get('password') or ''
        ok, msg = validate_login(username, password)
        if not ok:
            error = msg
        else:
            conn = get_db()
            user = conn.execute("SELECT * FROM pb_users WHERE username=?",
                                (username,)).fetchone()
            conn.close()
            # BUG-01：未区分"账号不存在"与"密码错误"（违反规则 2.1(5)(6)，
            #         预期 LOGIN_002、LOGIN_003 失败）
            if not user:
                error = '用户名或密码错误' if INJECT_DEFECTS else '账号不存在'
            elif not check_password_hash(user['password_hash'], password):
                error = '用户名或密码错误' if INJECT_DEFECTS else '密码错误'
            else:
                session['pb_user'] = username
                session['pb_user_id'] = user['id']
                return redirect(url_for('parabank.accounts'))
    return render_template('parabank/login.html', error=error)


@pb_bp.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    success = None
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        password = request.form.get('password') or ''
        confirm = request.form.get('confirm') or ''

        ok, msg = validate_register(username, password, confirm)
        if not ok:
            error = msg
        else:
            conn = get_db()
            exists = conn.execute("SELECT id FROM pb_users WHERE username=?",
                                  (username,)).fetchone()
            if exists:
                error = '用户名已存在'
                conn.close()
            else:
                conn.execute("INSERT INTO pb_users (username, password_hash) VALUES (?, ?)",
                             (username, generate_password_hash(password)))
                uid = conn.execute("SELECT id FROM pb_users WHERE username=?",
                                   (username,)).fetchone()['id']
                acc_num = str(20000 + uid)
                conn.execute("INSERT INTO pb_accounts (user_id, account_number, balance) VALUES (?, ?, ?)",
                             (uid, acc_num, 0.0))
                conn.commit()
                conn.close()
                success = '注册成功，请登录'
    return render_template('parabank/register.html', error=error, success=success)


@pb_bp.route('/accounts')
def accounts():
    if 'pb_user' not in session:
        return redirect(url_for('parabank.login'))
    conn = get_db()
    accs = conn.execute("SELECT * FROM pb_accounts WHERE user_id=? ORDER BY id",
                        (session['pb_user_id'],)).fetchall()
    conn.close()
    return render_template('parabank/accounts.html',
                           username=session['pb_user'],
                           accounts=[dict(a) for a in accs])


@pb_bp.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if 'pb_user' not in session:
        return redirect(url_for('parabank.login'))
    conn = get_db()
    error = None
    success = None

    if request.method == 'POST':
        from_acc = (request.form.get('from_account') or '').strip()
        to_acc = (request.form.get('to_account') or '').strip()
        amount_str = (request.form.get('amount') or '').strip()

        ok, amount, msg = validate_transfer(amount_str, from_acc, to_acc)
        if not ok:
            error = msg
        else:
            src = conn.execute("SELECT * FROM pb_accounts WHERE account_number=?",
                               (from_acc,)).fetchone()
            dst = conn.execute("SELECT * FROM pb_accounts WHERE account_number=?",
                               (to_acc,)).fetchone()
            if not src:
                error = '源账户不存在'
            elif not dst:
                error = '目标账户不存在'
            elif src['balance'] < amount:
                error = '账户余额不足'
            else:
                conn.execute("UPDATE pb_accounts SET balance=balance-? WHERE account_number=?",
                             (amount, from_acc))
                conn.execute("UPDATE pb_accounts SET balance=balance+? WHERE account_number=?",
                             (amount, to_acc))
                conn.execute("INSERT INTO pb_transactions (from_account, to_account, amount, txn_type, status) VALUES (?, ?, ?, 'TRANSFER', 'SUCCESS')",
                             (from_acc, to_acc, amount))
                conn.commit()
                success = ('转账成功: %s -> %s, 金额 %.2f 元'
                           % (from_acc, to_acc, amount))

    accs = conn.execute("SELECT * FROM pb_accounts WHERE user_id=? ORDER BY id",
                        (session['pb_user_id'],)).fetchall()
    conn.close()
    return render_template('parabank/transfer.html',
                           username=session['pb_user'],
                           accounts=[dict(a) for a in accs],
                           error=error, success=success)


@pb_bp.route('/transactions')
def transactions():
    if 'pb_user' not in session:
        return redirect(url_for('parabank.login'))
    conn = get_db()
    txs = conn.execute("SELECT * FROM pb_transactions ORDER BY id DESC LIMIT 50").fetchall()
    conn.close()
    return render_template('parabank/transactions.html',
                           username=session['pb_user'],
                           transactions=[dict(t) for t in txs])


@pb_bp.route('/logout')
def logout():
    session.pop('pb_user', None)
    session.pop('pb_user_id', None)
    return redirect(url_for('parabank.login'))
