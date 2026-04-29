import re
import glob
import os

def find_tabulars(tex):
    # Returns list of (start_idx, end_idx, tabular_text)
    matches = []
    for m in re.finditer(r'\\begin\{tabular\}.*?\\end\{tabular\}', tex, re.DOTALL):
        matches.append((m.start(), m.end(), m.group()))
    return matches

def count_cols_in_preamble(tabular_text):
    m = re.search(r'\\begin\{tabular\}\{([^\}]*)\}', tabular_text)
    if not m:
        return None, None
    colspec = m.group(1)
    # Only count column types (ignore | and spaces)
    ncols = len([c for c in colspec if c.lower() in "clrpmbxsq"])
    return colspec, ncols

def get_row_col_count(line):
    # Only consider lines that likely contain data (not \hline, \end, etc.)
    if '&' not in line or line.strip().startswith("\\"):
        return None
    # Remove LaTeX comments
    line = line.split('%')[0]
    # Only consider up to line break (\\)
    if '\\\\' in line:
        row = line.split('\\\\')[0]
    else:
        row = line
    # Count number of & for columns, add 1
    return row.count('&') + 1

def fix_tabular(tabular_text):
    # Get all rows
    lines = tabular_text.splitlines()
    row_col_counts = []
    for line in lines:
        count = get_row_col_count(line)
        if count is not None:
            row_col_counts.append(count)
    # Get the widest row
    if not row_col_counts:
        return tabular_text, False
    max_cols = max(row_col_counts)
    colspec, orig_cols = count_cols_in_preamble(tabular_text)
    if colspec is None or max_cols == orig_cols:
        return tabular_text, False
    # Rebuild column spec with same type as the first column
    default_type = next((c for c in colspec if c.lower() in "clrpmbxsq"), 'c')
    new_colspec = ''.join([default_type for _ in range(max_cols)])
    print(f"Fixing tabular: {orig_cols} → {max_cols} columns. ({colspec} → {new_colspec})")
    # Substitute new column spec in preamble
    fixed = re.sub(r'(\\begin\{tabular\})\{([^\}]*)\}', fr'\1{{{new_colspec}}}', tabular_text, count=1)
    return fixed, True

def process_tex_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        tex = f.read()
    matches = find_tabulars(tex)
    if not matches:
        return False
    changed = False
    new_tex = tex
    for start, end, tabular_text in reversed(matches):
        fixed_tabular, did_change = fix_tabular(tabular_text)
        if did_change:
            # Replace in the file
            new_tex = new_tex[:start] + fixed_tabular + new_tex[end:]
            changed = True
    if changed:
        os.rename(filename, filename + ".bak")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(new_tex)
        print(f"Fixed tabular environments in: {filename} (backup: {filename}.bak)")
    return changed

def main():
    for filename in glob.glob("**/*.tex", recursive=True):
        process_tex_file(filename)

if __name__ == "__main__":
    main()

