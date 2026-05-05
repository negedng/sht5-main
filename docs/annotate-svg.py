import sys, re
text_path, svg_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]

# Extract commits from text output (one per row, skip connector-only rows)
commits = []
graph_chars = set(' ●○│├┤─╯╮╰╭┴┼<>')
with open(text_path, encoding='utf-8') as f:
    for line in f:
        # Strip leading graph chars/spaces; what's left is "hash message [author]"
        i = 0
        while i < len(line) and line[i] in graph_chars:
            i += 1
        rest = line[i:].rstrip('\r\n')
        commits.append(rest)  # may be empty for connector rows

# Read SVG
with open(svg_path, encoding='utf-8') as f:
    svg = f.read()

# Find the max cx so we know where the lane diagram ends
cx_values = [int(m.group(1)) for m in re.finditer(r'cx="(\d+)"', svg)]
max_cx = max(cx_values) if cx_values else 30
text_x = max_cx + 30

# Generate <text> elements: one per commit row in text output (cy = 15 + index*15)
# but only for rows that ACTUALLY have a commit (text non-empty)
text_elems = []
commit_index = 0
for row_text in commits:
    if row_text:
        cy = 15 + commit_index * 15
        # Escape XML
        esc = row_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        text_elems.append(f'<text x="{text_x}" y="{cy + 4}" fill="#c4c4c4" font-family="monospace" font-size="11">{esc}</text>')
        commit_index += 1

# Estimate text width (rough: 7px per char, take longest)
max_text_len = max((len(c) for c in commits if c), default=0)
text_width = max_text_len * 7 + 20
new_width = text_x + text_width

# Update svg root tag
svg = re.sub(
    r'<svg[^>]+>',
    f'<svg height="{re.search(r"height=\"(\d+)\"", svg).group(1)}" '
    f'viewBox="0 0 {new_width} {re.search(r"viewBox=\"0 0 \d+ (\d+)\"", svg).group(1)}" '
    f'width="{new_width}" xmlns="http://www.w3.org/2000/svg">',
    svg, count=1
)

# Inject text elements before </svg>
svg = svg.replace('</svg>', '\n'.join(text_elems) + '\n</svg>')

with open(out_path, 'w', encoding='utf-8') as f:
    f.write(svg)
print(f"OK: {out_path}, {commit_index} commits, width={new_width}")
