#!/usr/bin/env python3
"""
ClashFX 配置修改工具

功能：
1. 备份原始配置文件
2. 从配置中提取有效代理节点，过滤掉无效节点和 >=5x 速节点
3. 生成自动选择策略组，插入到 proxy-groups 区域
"""

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

# ============ 手动配置区域 ============
# 配置文件路径
CONFIG_PATH = Path("/Users/tangxuan/Documents/jgjs-rules-modify/tests/jgjs.yaml")
# 新策略组名称
NEW_GROUP_NAME = "auto-select-no-high-speed"
# ====================================


def backup_config(config_path: Path) -> Path | None:
    """备份配置文件到同目录"""
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"{config_path.stem}_backup_{timestamp}{config_path.suffix}"
    backup_path = config_path.parent / backup_filename

    try:
        shutil.copy2(config_path, backup_path)
        print(f"配置文件已备份到: {backup_path}")
        return backup_path
    except PermissionError:
        print(f"警告: 无法备份配置文件到同目录，将备份到项目目录")
        project_backup_path = Path(__file__).parent / "backups" / backup_filename
        project_backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(config_path, project_backup_path)
        print(f"配置文件已备份到: {project_backup_path}")
        return project_backup_path


def parse_proxies(content: str) -> list[str]:
    """从配置文件中解析所有代理节点名称"""
    proxies: list[str] = []
    in_proxies_section = False
    indent_level = 0

    for line in content.splitlines():
        stripped = line.strip()

        if stripped.startswith("proxies:"):
            in_proxies_section = True
            indent_level = len(line) - len(line.lstrip())
            continue

        if in_proxies_section:
            current_indent = len(line) - len(line.lstrip())

            if current_indent <= indent_level and stripped and not stripped.startswith("#"):
                break

            if stripped.startswith("- name:"):
                name = stripped.split("- name:", 1)[1].strip().strip('"').strip("'")
                if name:
                    proxies.append(name)
            elif stripped.startswith("- {"):
                match = re.search(r"name:\s*(['\"])(.*?)\1", stripped)
                if match:
                    proxies.append(match.group(2))
                else:
                    match = re.search(r"name:\s*([^,{}]+?)\s*(,|})", stripped)
                    if match:
                        proxies.append(match.group(1).strip())

    return proxies


def filter_valid_proxies(proxies: list[str]) -> list[str]:
    """过滤掉无效节点和 >=5x 速节点"""
    INVALID_KEYWORDS = ["剩余流量", "距离下次重置", "套餐到期", "线路持续更新", "企业套餐"]
    INVALID_PREFIXES = ["⚠️", "⚡️", "🔥", "💡", "❌", "✅", "🔔", "📢"]

    filtered = []
    for p in proxies:
        if any(kw in p for kw in INVALID_KEYWORDS):
            continue
        if any(p.startswith(prefix) for prefix in INVALID_PREFIXES):
            continue
        match = re.search(r'-(\d+)x$', p, re.IGNORECASE)
        if match:
            speed = int(match.group(1))
            if speed >= 5:
                continue
        filtered.append(p)
    return filtered


def insert_policy_group(content: str, group_name: str, proxies: list[str]) -> str:
    """在 proxy-groups 区域内插入新策略组，并添加到 type: select 的策略组中"""
    if f"name: {group_name}" in content or f"name: '{group_name}'" in content or f'name: "{group_name}"' in content:
        print(f"策略组 '{group_name}' 已存在，跳过")
        return content

    lines = content.splitlines()
    in_proxy_groups = False
    indent_level = 0
    insert_index = -1
    select_group_line_index = -1

    for i, line in enumerate(lines):
        stripped = line.strip()

        if stripped.startswith("proxy-groups:"):
            in_proxy_groups = True
            indent_level = len(line) - len(line.lstrip())
            continue

        if in_proxy_groups:
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= indent_level and stripped and not stripped.startswith("#"):
                insert_index = i
                break
            if stripped.startswith("- {") and "name:" in stripped:
                insert_index = i
            if stripped.startswith("- {") and "type: select" in stripped:
                select_group_line_index = i

    if insert_index == -1:
        insert_index = len(lines)

    proxies_yaml = ", ".join([f"'{p}'" for p in proxies])
    new_group_lines = [
        "    - { name: " + NEW_GROUP_NAME + ", type: url-test, proxies: [" + proxies_yaml + "], url: 'http://www.gstatic.com/generate_204', interval: 86400 }"
    ]

    lines.insert(insert_index, new_group_lines[0])

    if select_group_line_index != -1:
        select_group_line = lines[select_group_line_index]
        if group_name in select_group_line:
            print(f"策略组 '{group_name}' 已添加到 select 策略组，跳过")
        else:
            match = re.search(r"(proxies:\s*\[)(.*?)(\])", select_group_line)
            if match:
                existing_proxies = match.group(2)
                if "自动选择" in existing_proxies:
                    new_proxies = existing_proxies.replace("自动选择", f"{group_name}, 自动选择")
                elif existing_proxies:
                    new_proxies = f"{existing_proxies}, {group_name}"
                else:
                    new_proxies = group_name
                lines[select_group_line_index] = select_group_line[:match.start(2)] + new_proxies + select_group_line[match.end(2):]

    return "\n".join(lines)


def main() -> int:
    """主函数"""
    print(f"读取配置文件: {CONFIG_PATH}")

    try:
        backup_dir = Path(__file__).parent / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"{CONFIG_PATH.stem}_backup_{timestamp}{CONFIG_PATH.suffix}"
        shutil.copy2(CONFIG_PATH, backup_path)
        print(f"配置文件已备份到: {backup_path}")

        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config_content = f.read()

        all_proxies = parse_proxies(config_content)
        print(f"共发现 {len(all_proxies)} 个节点")

        filtered_proxies = filter_valid_proxies(all_proxies)
        print(f"过滤后剩余 {len(filtered_proxies)} 个节点")

        if not filtered_proxies:
            print("没有找到需要保留的节点，无需生成策略组")
            return 0

        new_content = insert_policy_group(config_content, NEW_GROUP_NAME, filtered_proxies)

        if new_content == config_content:
            print("配置文件未发生变更")
            return 0

        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            f.write(new_content)

        print(f"\n策略组 '{NEW_GROUP_NAME}' 已插入到 proxy-groups 区域")
        print(f"配置文件已更新: {CONFIG_PATH}")
        print("\n完成!")
        return 0

    except FileNotFoundError as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1
    except PermissionError as e:
        print(f"权限错误: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"未知错误: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
