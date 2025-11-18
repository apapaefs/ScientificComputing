import re
import os
import glob
import json

def strip_math(text):
    """Replace $...$ or \( ... \) with just the math content (without LaTeX math)."""
    # Remove $...$
    text = re.sub(r'\$(.*?)\$', r'\1', text)
    # Remove \( ... \)
    text = re.sub(r'\\\((.*?)\\\)', r'\1', text)
    return text

def fix_markdown_headings(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    changed = False
    new_lines = []
    for line in lines:
        if re.match(r'^#+.*(\$.*\$|\\\(.*\\\))', line):
            new_line = strip_math(line)
            if new_line != line:
                print(f"Fixing markdown heading in {filename}: {line.strip()} -> {new_line.strip()}")
                changed = True
            new_lines.append(new_line)
        else:
            new_lines.append(line)
    if changed:
        os.rename(filename, filename + ".bak")
        with open(filename, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

def fix_latex_sections(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    def replacer(match):
        before = match.group(0)
        arg = match.group(2)
        fixed = strip_math(arg)
        after = f'\\{match.group(1)}{{{fixed}}}'
        if before != after:
            print(f"Fixing LaTeX {match.group(1)} in {filename}: {before.strip()} -> {after.strip()}")
        return after

    # \section{...}, \subsection{...}, \chapter{...}, \caption{...}, \label{...}
    pattern = re.compile(r'\\(section|subsection|chapter|caption|label)\{([^{}]*?(\$.*?\$|\\\(.*?\\\)).*?)\}')
    new_content = pattern.sub(replacer, content)

    if new_content != content:
        os.rename(filename, filename + ".bak")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(new_content)

def fix_ipynb_headings(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    changed = False
    for cell in data.get('cells', []):
        if cell.get('cell_type') == 'markdown':
            new_source = []
            for line in cell['source']:
                if re.match(r'^#+.*(\$.*\$|\\\(.*\\\))', line):
                    fixed = strip_math(line)
                    if fixed != line:
                        print(f"Fixing heading in notebook {filename}: {line.strip()} -> {fixed.strip()}")
                        changed = True
                    new_source.append(fixed)
                else:
                    new_source.append(line)
            cell['source'] = new_source
    if changed:
        os.rename(filename, filename + ".bak")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=1)

def main():
    # Adjust paths as needed
    for ext in ("md", "tex", "rst"):
        for filename in glob.glob(f"**/*.{ext}", recursive=True):
            if ext == "md" or ext == "rst":
                fix_markdown_headings(filename)
            elif ext == "tex":
                fix_latex_sections(filename)
    # For Jupyter notebooks
    for filename in glob.glob("**/*.ipynb", recursive=True):
        fix_ipynb_headings(filename)

if __name__ == "__main__":
    main()

