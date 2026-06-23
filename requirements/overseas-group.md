# 海外节点自动选择策略组

## 需求概述

新增一个包含所有海外节点（排除中国大陆节点）的自动选择策略组，与 `auto-select-no-high-speed` 策略组类似，但不过滤高速节点。

## 功能细节

1. **策略组名称**：`auto-select-overseas`
2. **过滤规则**：
   - 排除无效节点（剩余流量、距离下次重置等）
   - 排除中国大陆节点（名称含「🇨🇳中国」「内地」「大陆」「国内」等）
   - **不过滤高速节点**（保留所有 -5x、-10x 等）
3. **插入位置**：与 `auto-select-no-high-speed` 同级别，插入到 `proxy-groups` 区域
4. **关联策略组**：添加到 `type: select` 的策略组中，位于「自动选择」之前

## 配置项设计

```python
# 非高速自动选择策略组名称
NO_HIGH_SPEED_GROUP_NAME = "auto-select-no-high-speed"
# 海外节点自动选择策略组名称
OVERSEAS_GROUP_NAME = "auto-select-overseas"
```

## 实现要点

- 复用现有 `parse_proxies()` 和 `insert_policy_group()` 函数
- 新增 `filter_overseas_proxies()` 函数，只过滤无效节点和中国大陆节点
- 在 `main()` 中依次生成两个策略组
