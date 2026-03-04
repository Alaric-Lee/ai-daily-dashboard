import re

with open('docs/2026-03-04.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 检查每一行是否有特殊字符
for i, line in enumerate(lines, 1):
    # 查找HTML标签
    tags = re.findall(r'<[^>]+>', line)
    if tags:
        print(f"Line {i}: {tags}")
    
    # 查找可能的Vue问题字符
    if '<' in line and '>' in line:
        # 检查是否有未闭合的标签
        open_count = line.count('<')
        close_count = line.count('>')
        if open_count != close_count:
            print(f"Line {i} - Tag mismatch: open={open_count}, close={close_count}")
            print(f"  Content: {repr(line)}")

# 检查第107行附近
print("\n\nLines around 107:")
for i in range(100, min(115, len(lines))):
    print(f"{i+1}: {repr(lines[i])}")
