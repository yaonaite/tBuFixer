import os
from pathlib import Path

# 后缀字母映射（跳过 C）
def get_suffix(num: int) -> str:
    if num < 100:
        return 'A'
    elif num < 200:
        return 'B'
    elif num < 300:
        return 'D'
    elif num < 400:
        return 'E'
    elif num < 500:
        return 'F'
    elif num < 600:
        return 'G'
    elif num < 700:
        return 'H'
    elif num < 800:
        return 'I'
    elif num < 900:
        return 'J'
    elif num < 1000:
        return 'K'
    else:
        # 如果数字超出范围，默认不加后缀（按原样）
        return ''

def format_with_suffix(token: str) -> str:
    """
    根据原始字符串 token（可能最前面带零）和其数值，返回带后缀的字符串
    """
    try:
        value = int(token)
    except ValueError:
        # 如果不是数字，原样返回
        return token

    suffix = get_suffix(value)
    if suffix == '':
        return token  # 超范围不处理

    if value < 100:
        # 0-99：保留原字符串，直接加后缀
        return f"{token}{suffix}"
    else:
        # 100-999：去掉百位，保留后两位（含前导零），加后缀
        remainder = value % 100
        return f"{remainder:02d}{suffix}"

def process_line(tokens):
    """
    接收一行分割后的 7 个字符串列表，返回该行对应的两个块（字符串），块之间空一行
    """
    a, b, c, d, e, f, g = tokens

    # 原始块
    block1 = (
        f"DFIX 1.51 0.01 C{a} C{b} C{a} C{c} C{a} C{d}\n"
        f"DFIX 2.55 0.02 C{e} C{b} C{e} C{c} C{e} C{d}\n"
        f"DFIX 2.55 0.02 C{b} C{c} C{c} C{d} C{d} C{b}\n"
        f"DFIX 1.51 0.01 C{a} C{e}\n"
        f"DFIX 2.45 0.02 C{a} C{f} C{a} C{g}\n"
        f"EADP C{a} C{b} C{c} C{d}"
    )

    # 带后缀的四个数字
    a_s = format_with_suffix(a)
    b_s = format_with_suffix(b)
    c_s = format_with_suffix(c)
    d_s = format_with_suffix(d)

    # 后缀块 (e, f, g 保持原样)
    block2 = (
        f"DFIX 1.51 0.01 C{a_s} C{b_s} C{a_s} C{c_s} C{a_s} C{d_s}\n"
        f"DFIX 2.55 0.02 C{e} C{b_s} C{e} C{c_s} C{e} C{d_s}\n"
        f"DFIX 2.55 0.02 C{b_s} C{c_s} C{c_s} C{d_s} C{d_s} C{b_s}\n"
        f"DFIX 1.51 0.01 C{a_s} C{e}\n"
        f"DFIX 2.45 0.02 C{a_s} C{f} C{a_s} C{g}\n"
        f"EADP C{a_s} C{b_s} C{c_s} C{d_s}"
    )

    return block1 + "\n\n" + block2+ "\n"

def main():
    work_dir = Path(r"D:\forrings")
    if not work_dir.exists():
        print(f"目录不存在: {work_dir}")
        return

    # 匹配所有以 tbu.txt 结尾的文件（Windows下不区分大小写）
    for file_path in work_dir.glob("*tbu.txt"):
        out_path = work_dir / f"{file_path.stem}DFIX.txt"

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        output_blocks = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                # 跳过空行
                continue
            parts = stripped.split()
            if len(parts) != 7:
                print(f"警告: {file_path.name} 中的行 '{stripped}' 不是7个数字，已跳过")
                continue
            output_blocks.append(process_line(parts))

        # 每个块之间空一行（已在 process_line 中加好），整体用换行连接
        final_output = "\n".join(output_blocks) + "\n" if output_blocks else ""

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(final_output)

        print(f"已生成: {out_path.name}")

if __name__ == "__main__":
    main()