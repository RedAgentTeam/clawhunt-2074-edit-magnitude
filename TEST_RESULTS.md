# 测试结果

## 环境

- Python 3.12.14（Linux x86_64，glibc 2.41），依赖按 `pyproject.toml` 的 `.[test]` 全新安装
- 已安装版本：rapidfuzz 3.14.6、SQLAlchemy 2.1.9、pydantic 2.14.4、pytest 9.2.0、pytest-asyncio 1.5.0、aiosqlite 0.22.1、greenlet 3.5.6
- 运行时间：2026-11-25 07:34（Asia/Shanghai）

## 命令

```text
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
pytest -q -s
```

## 输出

```text
.5000 字对 5000 字：5 次计算最大耗时 0.003982 秒
.............................
30 passed in 0.34s
```

## 对照验收标准

1. 20 组以上夹具的 edit_ratio 与分档与期望一致：本包共 24 组夹具（文本 14、结构化 8、拒绝 2），全部通过。
2. 只改金额字段的结构化夹具 critical_edits 为 1：夹具 S01 通过。
3. 5000 字对 5000 字计算耗时 ≤ 200 ms：见上方输出中的最大耗时 0.003982 秒，`tests/test_perf.py` 断言通过。
4. 被拒绝的草稿不产生修改幅度记录：夹具 R01、R02 通过。
