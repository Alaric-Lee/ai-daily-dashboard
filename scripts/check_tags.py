import re

with open('docs/2026-03-04.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 统计所有HTML标签
open_tags = re.findall(r'<([a-zA-Z][a-zA-Z0-9]*)[^>]*(?<!/)>', content)
close_tags = re.findall(r'</([a-zA-Z][a-zA-Z0-9]*)>', content)
self_closing = re.findall(r'<([a-zA-Z][a-zA-Z0-9]*)[^>]*/>', content)

print(f'Opening tags: {len(open_tags)}')
print(f'Closing tags: {len(close_tags)}')
print(f'Self-closing tags: {len(self_closing)}')
print(f'\nOpen tags: {open_tags}')
print(f'\nClose tags: {close_tags}')

# 检查每个标签
from collections import Counter
open_count = Counter(open_tags)
close_count = Counter(close_tags)

print('\n\nTag balance check:')
all_tags = set(open_tags) | set(close_tags)
for tag in sorted(all_tags):
    o = open_count.get(tag, 0)
    c = close_count.get(tag, 0)
    if o != c:
        print(f'  {tag}: open={o}, close={c} - MISMATCH!')
    else:
        print(f'  {tag}: open={o}, close={c} - OK')
