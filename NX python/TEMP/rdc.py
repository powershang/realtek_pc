#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Usage: python rdc.py <verilog_file>

This script processes Verilog files to:
1. Find time delay patterns like '#100ns' and add display statements
2. Find calls to wait tasks and add display statements
3. Find calls to check tasks and add display statements

The modified content is saved to a new file with '.modified' extension.
"""
import re
import sys

def process_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 第一部分：处理延迟模式
    pattern_delay = r'^(\/\/)?[ \t]*(#(\d+)ns;?)([ \t]*\/\/.*)?$'
    
    index_delay = 0
    
    def replacement_delay(match):
        nonlocal index_delay
        index_delay += 1
        comment_prefix = match.group(1) or ''
        delay_stmt = match.group(2)
        delay_value = match.group(3)
        end_comment = match.group(4) or ''
        indent = re.match(r'^[ \t]*', match.string[match.start():]).group(0)
        display_prefix = '//' if comment_prefix else ''
        return f'{indent}{comment_prefix}{delay_stmt}{end_comment}\n{indent}{display_prefix}$display("HERE NEED DELAY #{index_delay}: {delay_value}ns");'
    
    modified_content = re.sub(pattern_delay, replacement_delay, content, flags=re.MULTILINE)
    
    # 第二部分：处理wait任务调用
    pattern_wait = r'^(\/\/)?[ \t]*(\b(?:mc_)?wait_[a-zA-Z0-9_]+\s*\([^;]*\);)([ \t]*\/\/.*)?$(?!.*task)'
    
    index_wait = 0
    
    def replacement_wait(match):
        nonlocal index_wait
        index_wait += 1
        comment_prefix = match.group(1) or ''
        wait_call = match.group(2)
        end_comment = match.group(3) or ''
        indent = re.match(r'^[ \t]*', match.string[match.start():]).group(0)
        display_prefix = '//' if comment_prefix else ''
        return f'{indent}{comment_prefix}{wait_call}{end_comment}\n{indent}{display_prefix}$display("HERE WAIT TASK CALL #{index_wait}: {wait_call.strip()}");'
    
    modified_content = re.sub(pattern_wait, replacement_wait, modified_content, flags=re.MULTILINE)
    
    # 第三部分：处理check任务调用
    pattern_check = r'^(\/\/)?[ \t]*(\bcheck_[a-zA-Z0-9_]+\s*\([^;]*\);)([ \t]*\/\/.*)?$(?!.*task)'
    
    index_check = 0
    
    def replacement_check(match):
        nonlocal index_check
        index_check += 1
        comment_prefix = match.group(1) or ''
        check_call = match.group(2)
        end_comment = match.group(3) or ''
        indent = re.match(r'^[ \t]*', match.string[match.start():]).group(0)
        display_prefix = '//' if comment_prefix else ''
        return f'{indent}{comment_prefix}{check_call}{end_comment}\n{indent}{display_prefix}$display("HERE CHECK TASK CALL #{index_check}: {check_call.strip()}");'
    
    modified_content = re.sub(pattern_check, replacement_check, modified_content, flags=re.MULTILINE)
    
    # 第四部分：处理 issue_mrw 调用
    pattern_issue_mrw = r'^(\/\/)?[ \t]*(issue_mrw\s*\([^;]*\);)([ \t]*\/\/.*)?$'
    
    index_issue_mrw = 0
    
    def replacement_issue_mrw(match):
        nonlocal index_issue_mrw
        index_issue_mrw += 1
        comment_prefix = match.group(1) or ''
        issue_mrw_call = match.group(2)
        end_comment = match.group(3) or ''
        indent = re.match(r'^[ \t]*', match.string[match.start():]).group(0)
        display_prefix = '//' if comment_prefix else ''
        return f'{indent}{comment_prefix}{issue_mrw_call}{end_comment}\n{indent}{display_prefix}$display("HERE ISSUE_MRW CALL #{index_issue_mrw}: {issue_mrw_call.strip()}");'
    
    modified_content = re.sub(pattern_issue_mrw, replacement_issue_mrw, modified_content, flags=re.MULTILINE)
    
    # 第五部分：处理 issue_mrr 调用
    pattern_issue_mrr = r'^(\/\/)?[ \t]*(issue_mrr\s*\([^;]*\);)([ \t]*\/\/.*)?$'
    
    index_issue_mrr = 0
    
    def replacement_issue_mrr(match):
        nonlocal index_issue_mrr
        index_issue_mrr += 1
        comment_prefix = match.group(1) or ''
        issue_mrr_call = match.group(2)
        end_comment = match.group(3) or ''
        indent = re.match(r'^[ \t]*', match.string[match.start():]).group(0)
        display_prefix = '//' if comment_prefix else ''
        return f'{indent}{comment_prefix}{issue_mrr_call}{end_comment}\n{indent}{display_prefix}$display("HERE ISSUE_MRR CALL #{index_issue_mrr}: {issue_mrr_call.strip()}");'
    
    modified_content = re.sub(pattern_issue_mrr, replacement_issue_mrr, modified_content, flags=re.MULTILINE)
    
    # 第六部分：處理 rbus_reg_set 調用
    # 修改模式以捕獲行尾註解
    pattern_rbus = r'^(\/\/)?[ \t]*(rbus_reg_set\s*\([^;]*\);)([ \t]*\/\/.*)?$'
    
    def replacement_rbus(match):
        comment_prefix = match.group(1) or ''  # 行首註解 //
        rbus_call = match.group(2)            # rbus_reg_set 調用
        end_comment = match.group(3) or ''    # 行尾註解
        indent = re.match(r'^[ \t]*', match.string[match.start():]).group(0)
        display_prefix = '//' if comment_prefix else ''
        return f'{indent}{comment_prefix}{rbus_call}{end_comment}\n{indent}{display_prefix}$display("[%0t] RBUS_REG_SET: {rbus_call.strip()}", $time);'
    
    modified_content = re.sub(pattern_rbus, replacement_rbus, modified_content, flags=re.MULTILINE)
    
    with open(filename + '.modified', 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print(f"Modified file saved as {filename}.modified")
    print(f"Added {index_delay} delay displays, {index_wait} wait task calls, {index_check} check task calls, {index_issue_mrw} issue_mrw calls, and {index_issue_mrr} issue_mrr calls")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <verilog_file>")
    else:
        process_file(sys.argv[1])