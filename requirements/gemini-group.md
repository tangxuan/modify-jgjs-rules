# Gemini 访问策略组需求

## 需求概述

新增一个专门用于访问 Gemini 的策略组，包含海外节点但排除越南节点。

## 功能细节

### 策略组名称
- `auto-select-gemini`

### 节点过滤规则

1. **排除无效节点**（与现有逻辑一致）：
   - 剩余流量提示（如「剩余流量：457.68 GB」）
   - 过期时间提示（如「过期时间：2025-05-21」）
   - 官网地址提示（如「官网地址：xxx.com」）
   - 节点更新提示（如「节点更新于：xxx」）

2. **排除中国大陆及香港节点**：
   - 包含 🇨🇳 表情符号
   - 包含关键词：中国、大陆、内地、国内、CN
   - 包含关键词：香港、深港

3. **排除越南节点**：
   - 包含 🇻🇳 表情符号
   - 包含关键词：越南、河内、胡志明

### 策略组配置

```yaml
- name: auto-select-gemini
  type: url-test
  proxies: [过滤后的节点列表]
  url: 'http://www.gstatic.com/generate_204'
  interval: 86400
```

### 插入位置

- 插入到 `proxy-groups` 区域
- 关联到 `type: select` 的策略组（如「极光加速」）
- 位置在 `auto-select-overseas` 之后

## 配置项

在 `jgjs_rules_modify.py` 中添加配置项：

```python
GEMINI_GROUP_NAME = "auto-select-gemini"
```

## 实现要点

1. 新增 `filter_gemini_proxies()` 函数，复用 `filter_overseas_proxies()` 的逻辑并增加越南节点过滤
2. 在 `main()` 函数中调用并生成策略组
3. 使用 `insert_policy_group()` 函数插入配置文件