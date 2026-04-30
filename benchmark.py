#!/usr/bin/env python3
"""
AI 大模型 50 分制基准测试工具
==============================
使用方法：
  1. 确保已安装 Python 3.7+（没有？看下方说明）
  2. 双击运行此文件，或在命令行执行：python benchmark.py
  3. 浏览器会自动打开测试页面

如果没有 Python：
  - 下载地址：https://www.python.org/downloads/
  - Windows 用户下载后安装，记得勾选 "Add Python to PATH"
  - 安装完成后重新运行此文件
"""

import http.server
import json
import threading
import webbrowser
import os
import sys
import urllib.request
import urllib.error
import time
import socket
import re
from pathlib import Path

# ==================== 检查 Python 版本 ====================
if sys.version_info < (3, 7):
    print("=" * 50)
    print("❌ Python 版本过低！")
    print(f"   当前版本: {sys.version}")
    print("   需要: Python 3.7 或更高版本")
    print("")
    print("📥 请到 https://www.python.org/downloads/ 下载最新 Python")
    print("=" * 50)
    input("按回车键退出...")
    sys.exit(1)

PORT = 18288

# ==================== 测试题目定义 ====================
TESTS = [
    {
        'id': 'constraints', 'name': '多约束执行', 'icon': '🎯',
        'prompt': '请只修改下面这段文字中的第 2 段，让它更简洁，但不要改动第 1 段和第 3 段的内容，也不要改变整体语气。\n\n【第1段】\n许多中小团队在选择 AI 供应商时，习惯直接对比模型名称与跑分排行，却忽略了服务层面的关键指标。CAP 理论提醒我们，系统在一致性、可用性与分区容错之间必须取舍，不同供应商的架构选择直接影响实际体验，光靠模型名字根本无从判断这些底层差异。\n\n【第2段】\n延迟与稳定性才是日常业务的真实痛点。某团队曾采购了一家主打顶级模型的供应商，结果高峰期响应时间超过 8 秒，接口频繁超时，导致产品上线后用户大量流失。这说明模型能力再强，若基础设施的稳定性不达标，对业务而言毫无意义。\n\n【第3段】\n中小团队资源有限，容错空间极小，一旦供应商出现延迟抖动或稳定性下降，损失往往难以承受。因此选型时必须关注 SLA 承诺、实际可用率、客服响应速度等运营指标，而非仅凭 CAP 层面的理论参数或品牌光环做决策。别只看招牌。'
    },
    {
        'id': 'code_fix', 'name': '代码修改', 'icon': '🐛',
        'prompt': "下面是一段已有代码，存在 bug 和边界问题。请只修复问题，不要改动无关逻辑；先解释 bug 原因，再给出修改后的完整代码；如果你改了额外内容，请明确列出来。\n\n```python\ndef summarize_scores(items):\n    total = 0\n    for item in items:\n        total += item['score']\n    avg = total / len(items)\n    passed = [x['name'] for x in items if x['score'] >= 60]\n    top = sorted(items, key=lambda x: x['score'])[0]['name']\n    return {\n        'avg': round(avg, 2),\n        'passed': passed,\n        'top': top,\n    }\n```"
    },
    {
        'id': 'reasoning', 'name': '复杂推理（海盗分金币）', 'icon': '🏴‍☠️',
        'prompt': '这是经典的海盗分金币博弈问题。5个海盗（A、B、C、D、E，按资历排序，A最老）要分配100枚金币。规则：\n1. 由最老的提出分配方案\n2. 所有人（包括提案人）投票，赞成票≥半数则通过\n3. 若不通过，提案人被扔下海，由下一位最老的继续提案\n4. 海盗都是绝对理性的，优先保命，其次多拿金币，再次希望看别人死\n\n请回答：\n1. A的最优分配方案是什么？（每人各得多少）\n2. 请用逆向推理过程完整解释\n3. 为什么更"平均"的方案（比如每人20枚）反而不优？'
    },
    {
        'id': 'longform', 'name': '长文结构化输出', 'icon': '📝',
        'prompt': '请写一篇 1200-1500 字的文章，主题：为什么中小团队选 AI 供应商时不能只看模型名。\n要求：\n- 字数严格控制在 1200-1500 字之间\n- 包含至少 3 个真实感强的案例/场景\n- 结构清晰，有小标题\n- 最后给出 3-5 条可执行的选型建议\n- 语气专业但易懂，面向技术决策者'
    },
    {
        'id': 'cn_dialog', 'name': '中文真实沟通', 'icon': '💬',
        'prompt': '帮我把这段内容改写成更适合发给熟人的版本。\n要求：自然、像人说话，不要太正式，不要写成客服腔，也不要过度热情。\n\n原文：\n"尊敬的用户，感谢您选择我们的服务。我们注意到您的账户即将到期，为确保您的正常使用，建议您尽快完成续费操作。如有任何疑问，欢迎随时联系我们的客服团队。"'
    },
    {
        'id': 'rewrite2', 'name': '二次改写/上下文衔接', 'icon': '✏️',
        'depends_on': 'cn_dialog',
        'prompt': '很好，这个版本已经不错了。但能不能再稍微调整一下：\n1. 加一点点轻松幽默的语气，但不要太夸张\n2. 把"续费"这个事儿说得委婉一点，别让用户觉得你在催钱\n3. 最后加一句表示"有空随时找我聊"的意思，但别说得太正式'
    },
    {
        'id': 'code_fix_2', 'name': '代码二次修改', 'icon': '🔧',
        'depends_on': 'code_fix',
        'prompt': "很好，这个版本修复了问题。现在我需要你再做一个小调整：\n1. 把返回的分数都改成整数（现在avg是小数）\n2. 添加一个功能：如果平均分低于60分，在返回结果里加一个字段 'warning': True\n3. 保持其他逻辑不变\n请给出修改后的完整代码，并说明改动点。"
    },
    {
        'id': 'factuality', 'name': '事实与幻觉控制', 'icon': '🔍',
        'prompt': '请回答下面问题：\n1. 如果你不确定，请直接说不确定。\n2. 不要编造来源。\n3. 把"你确定知道的"和"你不确定、需要验证的"分开写。\n\n问题：\n- OpenAI 的 GPT-5 模型是否已经正式发布？\n- Anthropic 的 Claude 4 最新版本号是什么？\n- 目前国内可用的 Claude 供应商有哪些主流选择？\n- 你认为这些供应商中哪家的性价比最高？（这是主观判断，请说明理由）'
    },
    {
        'id': 'implement', 'name': '编程能力专项', 'icon': '💻',
        'prompt': "请实现一个函数，满足以下规格：\n\n```python\ndef parse_log_line(line: str) -> dict:\n    \"\"\"\n    解析日志行，格式示例：\n    \"2024-03-15 14:23:45 [INFO] User login: username=alice, ip=192.168.1.100\"\n\n    返回字典格式：\n    {\n        'timestamp': '2024-03-15 14:23:45',\n        'level': 'INFO',\n        'event': 'User login',\n        'details': {'username': 'alice', 'ip': '192.168.1.100'}\n    }\n\n    要求：\n    1. 处理字段缺失的情况（如没有details）\n    2. 处理格式异常的情况（返回None或抛出异常）\n    3. 支持多种日志格式变体\n    4. 写清楚注释和边界处理说明\n    \"\"\"\n```"
    },
    {
        'id': 'multi_turn', 'name': '8轮多轮对话（长上下文）', 'icon': '📚',
        'multi_round': True,
        'rounds': [
            '先写一篇关于"AI辅助编程"的短介绍（200字左右）',
            '在上面的基础上，补充一个具体的使用场景案例',
            '继续补充，说明这个场景下AI具体能做什么、不能做什么',
            '现在把前面内容整理成一份给技术负责人的简报，突出ROI',
            '在简报最后加一段风险提示，说明AI编程的局限性',
            '把风险提示部分再细化一下，分点列出3-5个具体风险',
            '现在整个文档有点长了，帮我把案例部分压缩到原来的一半长度',
            '最后，总结一下当前版本和第一轮的初稿相比，主要改了哪些内容'
        ]
    }
]


# ==================== 评分函数 ====================
def score_item(test_id, text, ok):
    if not ok or not text:
        return 0, '失败'
    lower = text.lower()
    if test_id == 'constraints':
        # 原文段落
        p1_original = '许多中小团队在选择 AI 供应商时，习惯直接对比模型名称与跑分排行，却忽略了服务层面的关键指标。CAP 理论提醒我们，系统在一致性、可用性与分区容错之间必须取舍，不同供应商的架构选择直接影响实际体验，光靠模型名字根本无从判断这些底层差异。'
        p3_original = '中小团队资源有限，容错空间极小，一旦供应商出现延迟抖动或稳定性下降，损失往往难以承受。因此选型时必须关注 SLA 承诺、实际可用率、客服响应速度等运营指标，而非仅凭 CAP 层面的理论参数或品牌光环做决策。别只看招牌。'
        # 计算相似度（简单版：包含关键句子的比例）
        def similarity(original, text):
            # 提取关键句子（按句号分割）
            key_sentences = [s.strip() for s in original.split('。') if len(s.strip()) > 10]
            if not key_sentences:
                return 0
            matches = sum(1 for s in key_sentences if s[:20] in text)  # 前20字匹配
            return matches / len(key_sentences)
        sim_p1 = similarity(p1_original, text)
        sim_p3 = similarity(p3_original, text)
        # 如果第1段和第3段都保持高相似度（>0.5），且第2段有变化，则满分
        if sim_p1 >= 0.5 and sim_p3 >= 0.5 and len(text) < 300:
            return 5, f'多约束执行较好（P1相似度{sim_p1:.0%}, P3相似度{sim_p3:.0%}）'
        elif sim_p1 >= 0.3 and sim_p3 >= 0.3:
            return 4, f'基本满足约束（P1相似度{sim_p1:.0%}, P3相似度{sim_p3:.0%}）'
        else:
            return 3, f'可能改动过度，需人工核对（P1相似度{sim_p1:.0%}, P3相似度{sim_p3:.0%}）'
    if test_id == 'code_fix':
        if 'def summarize_scores' in text and ('max(' in text or '[-1]' in text or '最高分' in text) and ('空列表' in text or 'if not items' in text):
            return 5, '修复较完整'
        return 3, '部分完成'
    if test_id == 'reasoning':
        if '98' in text and ('C:1' in text or 'C：1' in text) and ('E:1' in text or 'E：1' in text or 'E:0' in text or 'E：0' in text):
            return 5, '答案正确'
        return 3, '需人工复核'
    if test_id == 'longform':
        if len(text) >= 1000 and ('建议' in text or '##' in text):
            return 5, f'长度约{len(text)}字符'
        return 3, '长度/结构可能不足'
    if test_id == 'cn_dialog':
        if '尊敬的用户' not in text and '客服团队' not in text:
            return 5, '自然度较好'
        return 3, '需人工复核语气'
    if test_id == 'rewrite2':
        if ('聊' in text or '唠' in text or '找我' in text) and ('续费' in text or '顺手' in text or '方便的话' in text):
            return 5, '二次修改接得住'
        return 3, '部分满足'
    if test_id == 'code_fix_2':
        if 'warning' in lower and ('int(' in text or 'round(' in text):
            return 5, '二次代码修改到位'
        return 3, '部分满足'
    if test_id == 'factuality':
        if ('不确定' in text or '需要验证' in text) and ('确定知道' in text or '不确定、需要验证' in text):
            return 5, '幻觉控制意识好'
        return 3, '有回答但区分不够清晰'
    if test_id == 'implement':
        if 'def parse_log_line' in text and ('return None' in text or 'raise' in text) and 'details' in text:
            return 5, '实现较完整'
        return 3, '实现需人工复核'
    if test_id == 'multi_turn':
        if '第一轮' in text or '初稿' in text or '短介绍' in text or '案例' in text:
            return 5, '长上下文保持正常'
        return 3, '可能有衰减'
    return 3, '默认人工复核'


# ==================== API 调用 ====================
def call_api(base_url, api_key, model, messages, protocol='openai', timeout=300, temperature=0.2):
    """调用 API，支持 Anthropic 和 OpenAI 协议，带端点自动探测"""
    started = time.time()
    
    if protocol == 'anthropic':
        # Anthropic 协议：尝试多个端点
        endpoints = get_anthropic_endpoints(base_url)
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        body = {'model': model, 'max_tokens': 8192, 'temperature': temperature, 'messages': messages}
        
        last_error = None
        for url in endpoints:
            try:
                req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers=headers, method='POST')
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    elapsed = round(time.time() - started, 2)
                    text = ''.join(b.get('text', '') for b in data.get('content', []) if b.get('type') == 'text')
                    return {'ok': True, 'text': text, 'elapsed': elapsed, 'error': None, 'url_used': url}
            except urllib.error.HTTPError as e:
                err_body = ''
                try: err_body = e.read().decode('utf-8')[:300]
                except: pass
                # 404 或 500 可能是端点不对，继续尝试下一个
                if e.code in [404, 500] and url != endpoints[-1]:
                    last_error = f'HTTP {e.code} on {url}'
                    continue
                # 429 限流，重试
                if e.code == 429:
                    time.sleep(10)
                    try:
                        req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers=headers, method='POST')
                        with urllib.request.urlopen(req, timeout=timeout) as resp:
                            data = json.loads(resp.read().decode('utf-8'))
                            elapsed = round(time.time() - started, 2)
                            text = ''.join(b.get('text', '') for b in data.get('content', []) if b.get('type') == 'text')
                            return {'ok': True, 'text': text, 'elapsed': elapsed, 'error': None, 'url_used': url}
                    except Exception as e2:
                        elapsed = round(time.time() - started, 2)
                        return {'ok': False, 'text': '', 'elapsed': elapsed, 'error': f'HTTP {e.code} after retry: {err_body}'}
                elapsed = round(time.time() - started, 2)
                return {'ok': False, 'text': '', 'elapsed': elapsed, 'error': f'HTTP {e.code}: {err_body}'}
            except Exception as e:
                last_error = str(e)
                continue
        
        # 所有端点都失败
        elapsed = round(time.time() - started, 2)
        return {'ok': False, 'text': '', 'elapsed': elapsed, 'error': f'All endpoints failed. Last: {last_error}'}
    
    else:
        # OpenAI 协议
        url = get_openai_endpoint(base_url)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        body = {'model': model, 'max_tokens': 8192, 'temperature': temperature, 'messages': messages}
        
        for attempt in range(3):
            try:
                req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers=headers, method='POST')
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    elapsed = round(time.time() - started, 2)
                    text = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                    return {'ok': True, 'text': text, 'elapsed': elapsed, 'error': None}
            except urllib.error.HTTPError as e:
                elapsed = round(time.time() - started, 2)
                err_body = ''
                try: err_body = e.read().decode('utf-8')[:300]
                except: pass
                if e.code == 429 and attempt < 2:
                    time.sleep(10)
                    continue
                return {'ok': False, 'text': '', 'elapsed': elapsed, 'error': f'HTTP {e.code}: {err_body}'}
            except Exception as e:
                elapsed = round(time.time() - started, 2)
                return {'ok': False, 'text': '', 'elapsed': elapsed, 'error': str(e)}
        return {'ok': False, 'text': '', 'elapsed': 0, 'error': 'Rate limited, retries exhausted'}


def detect_protocol(base_url, api_key, model):
    """自动检测协议，OpenAI 404时自动尝试 Anthropic"""
    # 先尝试 OpenAI
    try:
        res = call_api(base_url, api_key, model, [{'role': 'user', 'content': 'Hi'}], 'openai', timeout=30)
        if res['ok']:
            return 'openai'
        # 如果是 404 错误，自动尝试 Anthropic
        if '404' in (res.get('error') or ''):
            print(f"[检测] OpenAI 协议返回 404，尝试 Anthropic 协议...")
            try:
                res2 = call_api(base_url, api_key, model, [{'role': 'user', 'content': 'Hi'}], 'anthropic', timeout=30)
                if res2['ok'] or res2.get('error'):
                    return 'anthropic'
            except: pass
        # 其他错误但非 404，仍认为是 OpenAI
        return 'openai'
    except: pass
    # OpenAI 失败，尝试 Anthropic
    try:
        res = call_api(base_url, api_key, model, [{'role': 'user', 'content': 'Hi'}], 'anthropic', timeout=30)
        if res['ok'] or res.get('error'):
            return 'anthropic'
    except: pass
    return 'openai'


def clean_base_url(url):
    """智能清理 base URL，保留 /v1 路径"""
    url = url.strip()
    # 移除末尾的斜杠
    url = url.rstrip('/')
    # 如果 URL 以 /messages 或 /chat/completions 结尾，移除它们
    for suffix in ['/messages', '/chat/completions']:
        if url.endswith(suffix):
            url = url[:-len(suffix)]
            url = url.rstrip('/')
    return url


def get_anthropic_endpoints(base_url):
    """获取可能的 Anthropic 端点列表（按优先级排序）"""
    endpoints = []
    # 如果 base_url 已经包含 /v1，直接加 /messages
    if '/v1' in base_url:
        endpoints.append(f'{base_url}/messages')
    else:
        # 先尝试 /v1/messages (标准)，再试 /messages (兼容)
        endpoints.append(f'{base_url}/v1/messages')
        endpoints.append(f'{base_url}/messages')
    return endpoints


def get_openai_endpoint(base_url):
    """获取 OpenAI 兼容端点"""
    # 如果 URL 已经以 /v1, /v2, /v3, /v4 等版本号结尾，直接加 /chat/completions
    if re.search(r'/v\d+$', base_url):
        return f'{base_url}/chat/completions'
    # 否则尝试加 /v1/chat/completions
    return f'{base_url}/v1/chat/completions'


# ==================== 测试状态 ====================
test_state = {'running': False, 'results': [], 'responses': {}, 'protocol': None,
              'total': 0, 'current_test': '', 'progress': 0, 'error': None, 'done': False,
              'stop_requested': False, 'stopped': False, 'saved_inputs': {}}

def run_benchmark(base_url, api_key, model, forced_protocol=None, temperature=0.2):
    global test_state
    base_url = clean_base_url(base_url)
    test_state = {'running': True, 'results': [], 'responses': {}, 'protocol': None,
                  'total': 0, 'current_test': '检测协议中...', 'progress': 0, 'error': None, 'done': False, 'stopped': False,
                  'stop_requested': test_state.get('stop_requested', False), 'saved_inputs': test_state.get('saved_inputs', {})}
    try:
        if forced_protocol:
            protocol = forced_protocol
        else:
            protocol = detect_protocol(base_url, api_key, model)
        test_state['protocol'] = protocol
        test_state['current_test'] = f'协议: {protocol.upper()}'

        for i, test in enumerate(TESTS):
            if not test_state['running']:
                test_state['stopped'] = True
                break
            test_state['progress'] = i
            test_state['current_test'] = test['name']

            if test.get('multi_round'):
                convo, last_text, total_elapsed = [], '', 0
                for ri, rp in enumerate(test['rounds']):
                    if not test_state['running']:
                        test_state['stopped'] = True
                        break
                    test_state['current_test'] = f"{test['name']} · 轮次 {ri+1}/{len(test['rounds'])}"
                    convo.append({'role': 'user', 'content': rp})
                    res = call_api(base_url, api_key, model, convo, protocol, timeout=300, temperature=temperature)
                    total_elapsed += res.get('elapsed', 0)
                    if not res['ok']:
                        # 403 错误自动停止
                        if '403' in str(res.get('error', '')):
                            test_state['results'].append({'id': test['id'], 'name': test['name'], 'score': 0, 'note': '失败(403权限错误，已自动停止)', 'elapsed': total_elapsed, 'error': res['error'], 'text': ''})
                            test_state['running'] = False
                            test_state['stopped'] = True
                            break
                        test_state['results'].append({'id': test['id'], 'name': test['name'], 'score': 0, 'note': '失败', 'elapsed': total_elapsed, 'error': res['error'], 'text': ''})
                        break
                    last_text = res['text']
                    convo.append({'role': 'assistant', 'content': last_text})
                else:
                    score, note = score_item(test['id'], last_text, True)
                    test_state['results'].append({'id': test['id'], 'name': test['name'], 'score': score, 'note': note, 'elapsed': total_elapsed, 'error': None, 'text': last_text[:500]})
                    test_state['total'] += score

            elif test.get('depends_on'):
                prev = test_state['responses'].get(test['depends_on'], '')
                dep_test = next((t for t in TESTS if t['id'] == test['depends_on']), None)
                msgs = []
                if dep_test: msgs.append({'role': 'user', 'content': dep_test['prompt']})
                if prev: msgs.append({'role': 'assistant', 'content': prev})
                msgs.append({'role': 'user', 'content': test['prompt']})
                res = call_api(base_url, api_key, model, msgs, protocol, timeout=300, temperature=temperature)
                # 403 错误自动停止
                if not res['ok'] and '403' in str(res.get('error', '')):
                    score, note = 0, '失败(403权限错误，已自动停止)'
                    test_state['running'] = False
                    test_state['stopped'] = True
                else:
                    score, note = score_item(test['id'], res['text'], res['ok'])
                test_state['results'].append({'id': test['id'], 'name': test['name'], 'score': score, 'note': note, 'elapsed': res.get('elapsed', 0), 'error': res.get('error'), 'text': (res['text'] or '')[:500]})
                test_state['total'] += score
                if res['text']: test_state['responses'][test['id']] = res['text']
            else:
                res = call_api(base_url, api_key, model, [{'role': 'user', 'content': test['prompt']}], protocol, timeout=300, temperature=temperature)
                # 403 错误自动停止
                if not res['ok'] and '403' in str(res.get('error', '')):
                    score, note = 0, '失败(403权限错误，已自动停止)'
                    test_state['running'] = False
                    test_state['stopped'] = True
                else:
                    score, note = score_item(test['id'], res['text'], res['ok'])
                test_state['results'].append({'id': test['id'], 'name': test['name'], 'score': score, 'note': note, 'elapsed': res.get('elapsed', 0), 'error': res.get('error'), 'text': (res['text'] or '')[:500]})
                test_state['total'] += score
                if res['text']: test_state['responses'][test['id']] = res['text']
    except Exception as e:
        test_state['error'] = str(e)
    finally:
        test_state['running'] = False
        test_state['done'] = True
        test_state['progress'] = len(TESTS)


# ==================== HTTP 服务器 ====================
class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode('utf-8'))
        elif self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            state_out = {k: v for k, v in test_state.items() if k != 'responses'}
            self.wfile.write(json.dumps(state_out, ensure_ascii=False).encode('utf-8'))
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == '/api/start':
            content_length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(content_length).decode('utf-8'))
            # 保存输入以便停止后恢复
            test_state['saved_inputs'] = {'base_url': body.get('base_url',''), 'api_key': body.get('api_key',''), 'model': body.get('model',''), 'temperature': body.get('temperature', 0.2)}
            test_state['stop_requested'] = False
            test_state['stopped'] = False
            test_state['done'] = False
            test_state['running'] = True
            forced_protocol = body.get('forced_protocol')
            temp = float(body.get('temperature', 0.2)) if body.get('temperature') else 0.2
            thread = threading.Thread(target=run_benchmark, args=(body['base_url'], body['api_key'], body['model'], forced_protocol, temp))
            thread.daemon = True
            thread.start()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True}).encode('utf-8'))
        elif self.path == '/api/stop':
            test_state['stop_requested'] = True
            test_state['running'] = False
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True}).encode('utf-8'))
        elif self.path == '/api/shutdown':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True}).encode('utf-8'))
            threading.Thread(target=lambda: (time.sleep(0.5), server.shutdown()), daemon=True).start()
        else:
            self.send_error(404)

    def log_message(self, format, *args):
        pass  # Suppress default logging


HTML_PAGE = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI 大模型 50 分制基准测试</title>
<style>
.cb{display:flex;align-items:center;gap:8px;margin-top:12px;cursor:pointer}
.cb input{width:auto;margin:0}
.cb span{font-size:.85rem;color:var(--muted)}
.ta{width:100%;background:var(--input);border:1px solid var(--border);border-radius:8px;padding:10px 14px;color:var(--text);font-size:.85rem;outline:none;resize:vertical;min-height:80px;font-family:monospace}
.ta:focus{border-color:var(--blue)}
.hint{font-size:.8rem;color:var(--muted);margin-top:4px}
.err{color:var(--red);font-size:.85rem;margin-top:8px;display:none}
.err.act{display:block}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#0d1117;--card:#161b22;--input:#0d1117;--border:#30363d;--text:#e6edf3;--muted:#8b949e;--green:#3fb950;--blue:#58a6ff;--orange:#d29922;--red:#f85149;--r:12px}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans SC',sans-serif;background:var(--bg);color:var(--text);line-height:1.6;min-height:100vh}
.c{max-width:860px;margin:0 auto;padding:24px 20px 48px}
.hd{text-align:center;margin-bottom:32px}
.hd h1{font-size:1.75rem;font-weight:700;background:linear-gradient(135deg,var(--green),var(--blue));-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:8px}
.hd p{color:var(--muted);font-size:.9rem}
.card{background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:24px;margin-bottom:20px}
.fg{margin-bottom:16px}.fg:last-of-type{margin-bottom:0}
.fg label{display:block;font-size:.85rem;font-weight:600;color:var(--muted);margin-bottom:6px}
.fg input,.fg select{width:100%;background:var(--input);border:1px solid var(--border);border-radius:8px;padding:10px 14px;color:var(--text);font-size:.9rem;outline:none}
.fg input:focus,.fg select:focus{border-color:var(--blue)}
.iw{position:relative}
.tb{position:absolute;right:8px;top:50%;transform:translateY(-50%);background:none;border:none;color:var(--blue);cursor:pointer;font-size:.85rem}
.btn{width:100%;padding:12px;background:var(--green);color:#000;border:none;border-radius:8px;font-size:1rem;font-weight:700;cursor:pointer;margin-top:16px}
.btn:hover{opacity:.85}.btn:disabled{opacity:.5;cursor:not-allowed}
.btn.stop{background:var(--red);color:#fff}
.btn.stop:hover{opacity:.85}
.ps{display:none}.ps.act{display:block}
.pb{height:6px;background:var(--input);border-radius:3px;overflow:hidden;margin-bottom:10px}
.pf{height:100%;background:linear-gradient(90deg,var(--green),var(--blue));border-radius:3px;width:0;transition:width .3s}
.pi{display:flex;justify-content:space-between;font-size:.85rem;color:var(--muted)}
.ri{background:var(--card);border:1px solid var(--border);border-radius:var(--r);margin-bottom:12px;opacity:0;transform:translateY(8px);transition:all .3s}
.ri.vis{opacity:1;transform:none}
.rh{display:flex;align-items:center;justify-content:space-between;padding:14px 18px;cursor:pointer;user-select:none}
.rh:hover{background:rgba(255,255,255,.03)}
.rn{flex:1;margin:0 12px;font-size:.9rem}
.rs{font-weight:700;font-size:.9rem;padding:2px 10px;border-radius:4px}
.rs.s5{color:var(--green);background:rgba(63,185,80,.1)}.rs.s3{color:var(--orange);background:rgba(210,153,34,.1)}.rs.s0{color:var(--red);background:rgba(248,81,73,.1)}
.rm{display:flex;align-items:center;gap:10px;font-size:.8rem;color:var(--muted)}
.rb{max-height:0;overflow:hidden;transition:max-height .3s}.ri.open .rb{max-height:600px}
.rbi{padding:0 18px 18px;border-top:1px solid var(--border)}
.rbn{margin:12px 0;font-size:.85rem;color:var(--muted)}
.rbt{font-size:.8rem;color:var(--muted);white-space:pre-wrap;word-break:break-all;max-height:200px;overflow-y:auto;background:var(--input);padding:12px;border-radius:8px}
.sc{display:none;text-align:center}.sc.act{display:block}
.sb{font-size:3rem;font-weight:800;background:linear-gradient(135deg,var(--green),var(--blue));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.sm{font-size:1.2rem;color:var(--muted)}
.vd{margin-top:8px;font-size:1rem;font-weight:600}
.vd.t{color:var(--green)}.vd.g{color:var(--blue)}.vd.m{color:var(--orange)}.vd.w{color:var(--red)}
.be{display:inline-block;padding:8px 20px;margin-top:16px;background:var(--input);border:1px solid var(--border);color:var(--muted);border-radius:8px;cursor:pointer;font-size:.85rem}
.be:hover{border-color:var(--blue);color:var(--text)}
.ft{text-align:center;padding:24px 0 0;font-size:.8rem;color:#6e7681;border-top:1px solid var(--border);margin-top:32px}
.pb2{display:inline-block;padding:2px 10px;border-radius:4px;font-weight:700;font-size:.8rem;margin-left:8px}
.pb2.o{background:rgba(88,166,255,.15);color:var(--blue)}.pb2.a{background:rgba(63,185,80,.15);color:var(--green)}
</style>
</head>
<body>
<div class="c">
<div class="hd"><h1>AI 大模型 50 分制基准测试</h1><p>输入 API 信息，自动检测协议，跑完出总分。<br>基于本地 Python 服务，无 CORS 限制，Key 不经过第三方。</p></div>
<div class="card">
<div class="fg"><label>Base URL</label><input type="url" id="baseUrl" placeholder="https://api.openai.com/v1 或 https://openrouter.ai/api/v1/chat/completions"></div>
<div class="fg"><label>API Key</label><div class="iw"><input type="password" id="apiKey" placeholder="sk-..."><button class="tb" onclick="let i=document.getElementById('apiKey');i.type=i.type==='password'?'text':'password';this.textContent=i.type==='password'?'显示':'隐藏'">显示</button></div></div>
<div class="fg"><label>模型 ID</label><input type="text" id="modelId" placeholder="gpt-4o / claude-sonnet-4-20250514 / google/gemini-3.1-flash"></div>
<div class="fg"><label>协议类型（选填，留空自动识别）</label><select id="protocolSelect" style="width:100%;background:var(--input);border:1px solid var(--border);border-radius:8px;padding:10px 14px;color:var(--text);font-size:.9rem;outline:none"><option value="">自动识别</option><option value="openai">OpenAI</option><option value="anthropic">Anthropic</option></select></div>
<div class="fg"><label>Temperature（温度/随机性，选填，默认0.2）</label><input type="number" id="temperature" placeholder="0.2" step="0.1" min="0" max="2" value="0.2" style="width:120px"></div>
<div class="fg"><label>大模型提供商调用示例（用于取URL和协议，选填）</label><textarea class="ta" id="exampleCode" placeholder="粘贴 curl、Python 或 JavaScript 示例代码，例如：
curl https://api.example.com/v1/chat/completions \
  -H 'Authorization: Bearer sk-xxx' \
  -d '{\"model\": \"gpt-4o\", \"messages\": [{\"role\": \"user\", \"content\": \"Hello\"}]}'"></textarea><div class="hint">支持 curl、Python (requests/openai)、JavaScript 格式</div></div>
<div class="cb"><input type="checkbox" id="replaceModel"><span>用示例代码中的模型ID替换上方填写的模型ID</span></div>
<div class="err" id="parseErr">无法识别示例代码，请手动填写URL和协议</div>
<button class="btn" id="btnStart" onclick="startTest()">开始测试</button>
<button class="btn" id="btnStop" onclick="stopTest()" style="display:none;margin-top:8px;background:#f85149;color:#fff">停止测试</button>
</div>
<div class="card ps" id="ps"><div class="pb"><div class="pf" id="pf"></div></div><div class="pi"><span id="ct">准备中...</span><span id="pc">0 / 10</span></div></div>
<div id="pcCard" class="card" style="display:none;text-align:center;color:var(--muted);font-size:.9rem"><span id="pcMsg"></span></div>
<div id="rc"></div>
<div class="card sc" id="sc"><div class="sb" id="ts">0</div><div class="sm">/ 50</div><div class="vd" id="vd"></div><canvas id="radarChart" width="600" height="480" style="display:block;margin:20px auto;background:rgba(255,255,255,0.05);border-radius:12px;max-width:100%"></canvas><button class="be" onclick="exportMD()">导出 Markdown 报告</button></div>
<div class="ft">所有 API 调用通过本地 Python 服务转发，无 CORS 限制。<br>需要 Python 3.7+ 运行环境 | 如遇问题请确认已运行 python benchmark.py</div>
</div>
<script>
const TESTS=[
{id:'constraints',name:'多约束执行',icon:'🎯'},
{id:'code_fix',name:'代码修改',icon:'🐛'},
{id:'reasoning',name:'复杂推理（海盗分金币）',icon:'🏴\u200d☠️'},
{id:'longform',name:'长文结构化输出',icon:'📝'},
{id:'cn_dialog',name:'中文真实沟通',icon:'💬'},
{id:'rewrite2',name:'二次改写/上下文衔接',icon:'✏️'},
{id:'code_fix_2',name:'代码二次修改',icon:'🔧'},
{id:'factuality',name:'事实与幻觉控制',icon:'🔍'},
{id:'implement',name:'编程能力专项',icon:'💻'},
{id:'multi_turn',name:'8轮多轮对话（长上下文）',icon:'📚'}
];
let results=[];
function parseExample(){
const code=document.getElementById('exampleCode').value.trim();
if(!code)return{base_url:null,protocol:null,model:null};
let base_url=null,protocol='openai',model=null;
const urlMatch=code.match(/https?:\/\/[^\s\"'`]+/);
if(urlMatch){
let url=urlMatch[0];
if(url.includes('/chat/completions')){protocol='openai';base_url=url.split('/chat/completions')[0]}
else if(url.includes('/messages')){protocol='anthropic';base_url=url.split('/messages')[0]}
else if(url.includes('anthropic')){protocol='anthropic';base_url=url.replace(/\/$/,'')}
else if(url.includes('/v1/')){base_url=url.split('/v1/')[0]+'/v1'}
else{base_url=url.replace(/\/$/,'')}
}
// 支持多种格式：model="xxx", model='xxx', "model": "xxx", 'model': 'xxx'
const modelMatch=code.match(/["']?model["']?\s*[=:]\s*["']([^"']+)["']/);
if(modelMatch)model=modelMatch[1];
return{base_url,protocol,model};
}
function startTest(){
let b=document.getElementById('baseUrl').value.trim(),k=document.getElementById('apiKey').value.trim(),m=document.getElementById('modelId').value.trim();
const exampleCode=document.getElementById('exampleCode').value.trim();
const replaceModel=document.getElementById('replaceModel').checked;
const protocolSelect=document.getElementById('protocolSelect').value;
const parseErr=document.getElementById('parseErr');
parseErr.classList.remove('act');
// 优先使用手动选择的协议
if(protocolSelect){
window.forcedProtocol=protocolSelect;
}
if(exampleCode){
const parsed=parseExample();
if(parsed.base_url&&!b)b=parsed.base_url;
// 如果用户没有手动选择协议，才使用示例代码识别的协议
if(!protocolSelect&&parsed.protocol)window.forcedProtocol=parsed.protocol;
if(replaceModel&&parsed.model){m=parsed.model;document.getElementById('modelId').value=m}
else if(replaceModel&&!parsed.model){parseErr.textContent='示例代码中未找到模型ID，请手动填写或取消勾选';parseErr.classList.add('act');return}
if(!b&&!parsed.base_url){parseErr.textContent='无法识别示例代码中的URL，请手动填写';parseErr.classList.add('act');return}
}
if(!b||!k||!m){alert('请填写所有字段');return}
const btn=document.getElementById('btnStart');btn.disabled=true;btn.textContent='测试中...';
document.getElementById('btnStop').style.display='block';document.getElementById('btnStop').disabled=false;document.getElementById('btnStop').textContent='停止测试';document.getElementById('btnStop').disabled=false;document.getElementById('btnStop').textContent='停止测试';
results=[];document.getElementById('rc').innerHTML='';document.getElementById('sc').classList.remove('act');
document.getElementById('ps').classList.add('act');document.getElementById('pcCard').style.display='none';
// 保存表单状态
window._savedForm={baseUrl:b,apiKey:k,modelId:m,temperature:document.getElementById('temperature').value||'0.2'};
const body={base_url:b,api_key:k,model:m,temperature:parseFloat(document.getElementById('temperature').value)||0.2};
if(window.forcedProtocol)body.forced_protocol=window.forcedProtocol;
fetch('/api/start',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)})
.then(r=>r.json()).then(d=>{
if(d.error){alert('启动失败: '+d.error);btn.disabled=false;btn.textContent='开始测试';return}
poll();
}).catch(e=>{alert('请求失败: '+e.message+'\n\n请确认 Python 脚本正在运行');btn.disabled=false;btn.textContent='开始测试'});
}
function stopTest(){
const btn=document.getElementById('btnStop');btn.disabled=true;btn.textContent='停止中...';
fetch('/api/stop',{method:'POST',headers:{'Content-Type':'application/json'}}).catch(()=>{});
}
function restoreForm(){
const s=window._savedForm;
if(s){document.getElementById('baseUrl').value=s.baseUrl||'';document.getElementById('apiKey').value=s.apiKey||'';document.getElementById('modelId').value=s.modelId||'';document.getElementById('temperature').value=s.temperature||'0.2';}
}
function poll(){
fetch('/api/status').then(r=>r.json()).then(d=>{
document.getElementById('pf').style.width=(d.progress/10*100)+'%';
document.getElementById('ct').textContent=d.current_test||'...';
document.getElementById('pc').textContent=d.progress+' / 10';
if(d.protocol){
document.getElementById('pcCard').style.display='block';
document.getElementById('pcMsg').innerHTML='协议: <span class="pb2 '+(d.protocol==='anthropic'?'a':'o')+'">'+d.protocol.toUpperCase()+'</span>';
}
const c=document.getElementById('rc');
if(d.results.length>c.children.length){
c.innerHTML='';
d.results.forEach((r,i)=>{
const t=TESTS[i],ic=r.score>=5?'✅':(r.score>=3?'⚠️':'❌'),cl=r.score>=5?'s5':(r.score>=3?'s3':'s0');
const div=document.createElement('div');div.className='ri'+(r.score===0?' open':'');
let errorMsg=r.error?esc(r.error):'';if(errorMsg.includes('404')){errorMsg+=' <span style="color:var(--yellow)">💡 提示: 404错误可能是协议不匹配，请尝试在"协议类型"中选择 Anthropic</span>'}div.innerHTML='<div class="rh" onclick="this.parentElement.classList.toggle(\'open\')"><span>'+ic+'</span><span class="rn">'+t.icon+' '+t.name+'</span><span class="rs '+cl+'">'+r.score+'/5</span><span class="rm"><span>'+r.elapsed.toFixed(1)+'s</span><span>\u25bc</span></span></div><div class="rb"><div class="rbi"><div class="rbn">\ud83d\udcdd '+r.note+(errorMsg?' \xb7 \u26a0\ufe0f '+errorMsg:'')+'</div><div class="rbt">'+esc(r.text||'(无回复)')+'</div></div></div>';
c.appendChild(div);requestAnimationFrame(()=>div.classList.add('vis'));
});
}
if(d.done){
document.getElementById('pf').style.width='100%';
document.getElementById('ct').textContent=d.stopped?'已停止':'测试完成';
document.getElementById('ps').classList.remove('act');
const tot=d.total;document.getElementById('ts').textContent=tot;
if(d.stopped){restoreForm();}
let v,vc;if(tot>=45){v='\ud83c\udfc6 顶级水平';vc='t'}else if(tot>=40){v='\ud83c\udf1f 优秀';vc='g'}else if(tot>=30){v='\ud83d\udc4d 中等';vc='m'}else{v='\u26a0\ufe0f 偏弱';vc='w'}
const ve=document.getElementById('vd');ve.textContent=v;ve.className='vd '+vc;
document.getElementById('sc').classList.add('act');results=d.results;
// 绘制雷达图
setTimeout(()=>drawRadarChart(d.results),100);
const btn=document.getElementById('btnStart');btn.disabled=false;btn.textContent='重新测试';
document.getElementById('btnStop').style.display='none';
}else{setTimeout(poll,1000)}
}).catch(()=>setTimeout(poll,2000));
}
function esc(t){const d=document.createElement('div');d.textContent=t;return d.innerHTML}
function exportMD(){
const m=document.getElementById('modelId').value.trim();
const b=document.getElementById('baseUrl').value.trim();
const t=results.reduce((s,r)=>s+r.score,0);
// 从URL提取供应商名字
let provider='unknown';
if(b){
const match=b.match(/https?:\/\/([^\/]+)/);
if(match){
let host=match[1];
// 去掉 api. www. 前缀
host=host.replace(/^api\./,'').replace(/^www\./,'');
// 取主域名（去掉 .com .cn 等后缀）
const parts=host.split('.');
if(parts.length>=2)provider=parts[parts.length-2];
}
}
// 获取雷达图 base64
const canvas=document.getElementById('radarChart');
let radarImg='';
if(canvas){radarImg='![雷达图]('+canvas.toDataURL('image/png')+')\n\n';}
// 计算各维度得分
const dimScores=GROUPS.map(g=>{const s=g.indices.map(i=>results[i].score);return(s.reduce((a,b)=>a+b,0)/s.length).toFixed(1);});
let md='# AI 大模型基准测试报告\n\n'+radarImg+'- **模型**: '+m+'\n- **供应商**: '+provider+'\n- **总分**: '+t+'/50\n- **时间**: '+new Date().toLocaleString('zh-CN')+'\n\n## 各维度得分\n\n| 维度 | 得分 | 说明 |\n|------|------|------|\n';
GROUPS.forEach((g,i)=>{md+='| '+g.name+' | '+dimScores[i]+'/5 | '+g.desc+' |\n';});
md+='\n## 详细测试结果\n\n| # | 测试项 | 得分 | 耗时 | 备注 |\n|---|--------|------|------|------|\n';
results.forEach((r,i)=>{md+='| '+(i+1)+' | '+TESTS[i].name+' | '+r.score+'/5 | '+r.elapsed.toFixed(1)+'s | '+r.note+' |\n';});
const blob=new Blob([md],{type:'text/markdown'});const a=document.createElement('a');
a.href=URL.createObjectURL(blob);a.download='benchmark-'+provider+'-'+m.replace(/\//g,'-')+'-'+Date.now()+'.md';a.click();
}
// 测试分组定义
const GROUPS=[
{name:'💻代码能力',indices:[1,6,8],desc:'代码修改+二次修改+编程专项'},
{name:'🧠推理分析',indices:[2,7],desc:'复杂推理+事实控制'},
{name:'📝语言表达',indices:[3,4],desc:'长文输出+中文沟通'},
{name:'✏️上下文处理',indices:[5,9],desc:'改写衔接+多轮对话'},
{name:'🎯综合执行',indices:[0],desc:'多约束执行'}
];
function drawRadarChart(results){
const canvas=document.getElementById('radarChart');
if(!canvas)return;
const ctx=canvas.getContext('2d');
const w=canvas.width,h=canvas.height-40;
const cx=w/2,cy=h/2+10;
const r=Math.min(w,h)/2-50;
const n=GROUPS.length;
const maxScore=5;
// 计算每组得分
const groupScores=GROUPS.map(g=>{
const scores=g.indices.map(i=>results[i].score);
return scores.reduce((a,b)=>a+b,0)/scores.length;
});
// 清空画布
ctx.clearRect(0,0,w,h+40);
// 绘制背景网格（5层）
ctx.strokeStyle='rgba(255,255,255,0.1)';ctx.lineWidth=1;
for(let i=1;i<=5;i++){
ctx.beginPath();
for(let j=0;j<n;j++){
const angle=j*2*Math.PI/n-Math.PI/2;
const pr=r*i/5;
const x=cx+pr*Math.cos(angle);
const y=cy+pr*Math.sin(angle);
if(j===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);
}
ctx.closePath();ctx.stroke();
}
// 绘制轴线
for(let i=0;i<n;i++){
const angle=i*2*Math.PI/n-Math.PI/2;
ctx.beginPath();ctx.moveTo(cx,cy);
ctx.lineTo(cx+r*Math.cos(angle),cy+r*Math.sin(angle));ctx.stroke();
}
// 绘制数据区域
ctx.fillStyle='rgba(74,222,128,0.3)';ctx.strokeStyle='#4ade80';ctx.lineWidth=2;
ctx.beginPath();
for(let i=0;i<n;i++){
const angle=i*2*Math.PI/n-Math.PI/2;
const score=groupScores[i];
const pr=r*score/maxScore;
const x=cx+pr*Math.cos(angle);
const y=cy+pr*Math.sin(angle);
if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);
}
ctx.closePath();ctx.fill();ctx.stroke();
// 绘制数据点
for(let i=0;i<n;i++){
const angle=i*2*Math.PI/n-Math.PI/2;
const score=groupScores[i];
const pr=r*score/maxScore;
const x=cx+pr*Math.cos(angle);
const y=cy+pr*Math.sin(angle);
ctx.fillStyle=score>=4?'#4ade80':(score>=2?'#facc15':'#f87171');
ctx.beginPath();ctx.arc(x,y,5,0,2*Math.PI);ctx.fill();
// 显示分数
ctx.fillStyle='#fff';ctx.font='bold 10px sans-serif';
ctx.fillText(score.toFixed(1),x+8,y-8);
}
// 绘制标签（错开位置避免重叠）
ctx.fillStyle='#fff';ctx.font='bold 13px sans-serif';ctx.textBaseline='middle';
for(let i=0;i<n;i++){
const angle=i*2*Math.PI/n-Math.PI/2;
const label=GROUPS[i].name;
// 根据角度调整标签位置和对齐方式
let lx,ly,textAlign;
if(angle>-Math.PI/4&&angle<Math.PI/4){// 右侧
lx=cx+(r+35)*Math.cos(angle);ly=cy+(r+35)*Math.sin(angle);textAlign='left';
}else if(angle>=Math.PI/4&&angle<3*Math.PI/4){// 下方
lx=cx+(r+30)*Math.cos(angle);ly=cy+(r+45)*Math.sin(angle);textAlign='center';
}else if(angle>=3*Math.PI/4||angle<-3*Math.PI/4){// 左侧
lx=cx+(r+35)*Math.cos(angle);ly=cy+(r+35)*Math.sin(angle);textAlign='right';
}else{// 上方
lx=cx+(r+30)*Math.cos(angle);ly=cy+(r+30)*Math.sin(angle);textAlign='center';
}
ctx.textAlign=textAlign;
ctx.fillText(label,lx,ly);
}
// 绘制分组说明
ctx.fillStyle='rgba(255,255,255,0.5)';ctx.font='9px sans-serif';ctx.textAlign='center';
let descY=h+15;
ctx.fillText('💻代码:代码修改+二次修改+编程 | 🧠推理:复杂推理+事实控制 | 📝语言:长文输出+中文沟通',w/2,descY);
ctx.fillText('✏️上下文:改写衔接+多轮对话 | 🎯综合:多约束执行',w/2,descY+12);
}
// 浏览器关闭时自动退出服务
window.addEventListener('beforeunload',function(){navigator.sendBeacon('/api/shutdown');});
</script>
</body>
</html>'''


# ==================== 启动 ====================
def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

class ThreadedHTTPServer(http.server.ThreadingHTTPServer):
    daemon_threads = True

if __name__ == '__main__':
    port = PORT
    # Try the default port, fall back to a random one
    try:
        server = ThreadedHTTPServer(('127.0.0.1', port), Handler)
    except OSError:
        port = find_free_port()
        server = ThreadedHTTPServer(('127.0.0.1', port), Handler)

    url = f'http://localhost:{port}'
    print('=' * 50)
    print('🦞 AI 大模型 50 分制基准测试工具')
    print('=' * 50)
    print(f'  服务已启动: {url}')
    print(f'  浏览器即将自动打开...')
    print(f'  按 Ctrl+C 停止服务')
    print('=' * 50)

    webbrowser.open_new_tab(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n服务已停止')
        server.server_close()
