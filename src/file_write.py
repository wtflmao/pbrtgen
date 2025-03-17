def overwrite_file(filepath, content):
    """覆盖写入文件。"""
    with open(filepath, 'w') as f:  # 使用 'w' 模式打开文件
        f.write(content)

def append_to_file(filepath, content):
    """向文件追加内容。"""
    with open(filepath, 'a') as f:  # 使用 'a' 模式打开文件
        f.write(content)

def write_lines_to_file_loop_with_newline(filepath, string_list):
    """使用循环和 write() 将字符串列表写入文件。"""
    with open(filepath, 'a') as f:
        for line in string_list:
            f.write(line + '\n')  # 在每行末尾添加换行符

def write_line_to_file_loop_with_newline(filepath, line):
    """使用循环和 write() 将字符串列表写入文件。"""
    with open(filepath, 'a') as f:
        f.write(line + '\n')  # 在每行末尾添加换行符