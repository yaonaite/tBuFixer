import os
import re
from pathlib import Path

# ---------- 后缀字母规则（跳过 C） ----------
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
        return ''   # 超出范围不处理

def format_atom_suffix(atom_num: int) -> str:
    """将原子编号转换为带后缀的字符串，如 174 -> '74B' """
    suffix = get_suffix(atom_num)
    if suffix == '':
        return str(atom_num)      # 无后缀
    if atom_num < 100:
        return f"{atom_num:02d}{suffix}"
    else:
        remainder = atom_num % 100
        return f"{remainder:02d}{suffix}"

# ---------- 解析 .ins 文件中的碳原子行 ----------
def parse_ins_atoms(ins_path):
    """
    返回字典：{ 原子序号: (line1, line2) }
    line1 是第一行（不含末尾换行），line2 是续行（不含换行），没有续行则为 None
    """
    with open(ins_path, 'r') as f:
        lines = f.readlines()

    atoms = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        # 匹配以 C 开头后跟数字的原子行（允许前导空格）
        match = re.match(r'^(\s*C)(\d+)', line)
        if match:
            atom_num = int(match.group(2))
            line1 = line.rstrip('\n')
            line2 = None
            # 如果行末有续行标志 "="，则读取下一行
            if line1.rstrip().endswith('='):
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    # 续行通常以空白开头，直接采用
                    line2 = next_line.rstrip('\n')
                    i += 1          # 跳过续行
            atoms[atom_num] = (line1, line2)
        i += 1
    return atoms

# ---------- 生成一个 PART 块 ----------
def process_ins_part(atom_info_dict, part_label, atom_nums, suffix_map=None):
    """
    根据原子信息字典和四个原子序号，生成 PART part_label 的字符串。
    suffix_map: 如果是 PART 2，传入 {atom_num: new_suffix_str}，否则为 None。
    """
    output_lines = [f"PART {part_label}"]
    for num in atom_nums:
        line1, line2 = atom_info_dict[num]
        # 1) 占用率 11.00000 -> 10.50000
        line1_mod = re.sub(r'\b11\.00000\b', '10.50000', line1)
        # 2) 如果是 PART 2，替换原子名
        if suffix_map is not None:
            new_suffix = suffix_map[num]      # 例如 '74B'
            # 将 C后跟数字 的部分替换为 C+新后缀
            line1_mod = re.sub(r'^(\s*C)\d+', r'\g<1>' + new_suffix, line1_mod)
        # 3) 去掉行尾的续行标志 "=" 并补一个空格
        line1_mod = re.sub(r'\s*=\s*$', ' ', line1_mod)
        output_lines.append(line1_mod)
        if line2 is not None:
            output_lines.append(line2)
    return '\n'.join(output_lines)

# ---------- 主程序 ----------
def main():
    work_dir = Path(r"D:\forrings")
    if not work_dir.exists():
        print(f"目录不存在: {work_dir}")
        return

    ins_files = list(work_dir.glob("*.ins"))
    if not ins_files:
        print("没有找到 .ins 文件")
        return

    # 建立 tbu 文件映射（小写文件名 -> 路径）
    tbu_map = {}
    for f in work_dir.iterdir():
        if f.is_file() and f.name.lower().endswith('tbu.txt'):
            tbu_map[f.name.lower()] = f

    for ins_path in ins_files:
        stem = ins_path.stem               # 不含扩展名的文件名
        tbu_key = stem.lower() + 'tbu.txt' # 例如 a.ins -> atbu.txt
        if tbu_key not in tbu_map:
            print(f"警告: 找不到对应的 tbu 文件: {tbu_key}，跳过 {ins_path.name}")
            continue
        tbu_path = tbu_map[tbu_key]

        # 解析 ins 中的碳原子
        atoms = parse_ins_atoms(ins_path)
        if not atoms:
            print(f"警告: {ins_path.name} 中未找到碳原子，跳过")
            continue

        # 读取 tbu 文件中的数字行
        with open(tbu_path, 'r') as f:
            tbu_lines = f.readlines()

        out_path = work_dir / f"{stem}tbuPART.txt"
        with open(out_path, 'w') as out:
            for line in tbu_lines:
                stripped = line.strip()
                if not stripped:
                    continue
                parts = stripped.split()
                if len(parts) != 7:
                    print(f"警告: {tbu_path.name} 中行 '{stripped}' 不是7个数字，跳过")
                    continue

                # 前四个数字是碳原子编号
                atom_nums = [int(x) for x in parts[:4]]
                # 检查是否都在 ins 中出现
                missing = [n for n in atom_nums if n not in atoms]
                if missing:
                    print(f"错误: 在 {ins_path.name} 中找不到原子 C{missing}，对应行: {stripped}")
                    continue

                # 准备 PART 2 的后缀映射
                suffix_map = {n: format_atom_suffix(n) for n in atom_nums}

                # 生成 PART 1 和 PART 2，并以 PART 0 结束该组
                part1 = process_ins_part(atoms, 1, atom_nums)
                part2 = process_ins_part(atoms, 2, atom_nums, suffix_map=suffix_map)

                out.write(part1 + "\n\n")
                out.write(part2 + "\n\n")
                out.write("PART 0\n\n")   # 组结束，块间保留空行

        print(f"已生成: {out_path.name}")

if __name__ == "__main__":
    main()