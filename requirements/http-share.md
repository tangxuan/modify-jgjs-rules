# HTTP 共享功能需求

## 需求概述

通过 Python 3 内置 HTTP 服务器，在 8080 端口共享指定目录路径的文件。

## 功能细节

1. **配置项控制**：新增配置项 `ENABLE_HTTP_SHARE`（bool），默认 `False`。设为 `True` 时启用 HTTP 共享。
2. **共享目录**：使用 `CONFIG_PATH` 的父目录作为共享根目录。
3. **端口**：固定 8080。
4. **启动方式**：在脚本末尾（所有修改完成后）启动 HTTP 服务器。
5. **服务器类型**：使用 Python 标准库 `http.server`，无需额外依赖。

## 配置项设计

```python
# ============ 手动配置区域 ============
# 配置文件路径
CONFIG_PATH = Path("/Users/tangxuan/.config/clashfx/jgjs.yaml")
# 新策略组名称
NEW_GROUP_NAME = "auto-select-no-high-speed"
# HTTP 共享开关（启用后会在 8080 端口共享配置目录）
ENABLE_HTTP_SHARE = False
# ====================================
```

## 行为

- `ENABLE_HTTP_SHARE = True`：修改完成后，在 8080 端口启动 HTTP Server，共享 `CONFIG_PATH.parent`
- `ENABLE_HTTP_SHARE = False`（默认）：不启动 HTTP Server，行为与之前一致

## 实现要点

- 使用 `http.server.HTTPServer` + `SimpleHTTPRequestHandler`
- 在独立线程中启动，避免阻塞脚本退出
- 启动后打印访问地址（如 `http://localhost:8080`）
- 捕获 `KeyboardInterrupt` 以优雅退出
