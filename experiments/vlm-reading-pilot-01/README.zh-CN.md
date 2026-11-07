# 试验 01：旋转汉字的视觉语言模型盲测

[English](README.md) · [English Results](RESULTS.md) · [中文结果](RESULTS.zh-CN.md)

**研究状态：**探索性、可复核的预实验；**不能据此证明人类可读性，也不能作为合并实验分支的充分依据**。

## 研究目的与设计

本试验使用 **52 张二值字形图像**，对应 26 个图形、每个图形两个方向，并由四种视觉语言模型分别识读，共安排 **208 次模型×图像测试**。五个自旋转字形在四种条件下比较：历史主分支、笔画半宽修正、R-ODD、谐波场。两个不同字符的配对在三种条件下比较：历史主分支、修正半宽后的简单合并、A/B 笔画融合。

自旋转与异字配对是不同研究任务，**不得将两者混合成一个算法排名**。测试字符属于事先选择的演示样本，不是独立留出集；没有人类读者参与。

## 文件说明

- [PROTOCOL.md](PROTOCOL.md)：逐字提示词、会话隔离、数据解析和偏差记录。
- [RESULTS.md](RESULTS.md) 与 [RESULTS.zh-CN.md](RESULTS.zh-CN.md)：评分结果、局限和解释。
- [data/responses_matrix.csv](data/responses_matrix.csv)：四个模型对 52 个试次的原始短文本结果；`INVALID` 和 `ERROR` 表示空输出的状态编码，不是模型实际输出的字符串；`UNKNOWN` 为模型实际输出。
- [data/ground_truth.csv](data/ground_truth.csv)：测试编号、算法条件、方向、目标字符的映射；**不可向接受盲测的模型提供**。
- [scripts/score.py](scripts/score.py)：仅使用 Python 标准库的评分程序。
- [scripts/test_score.py](scripts/test_score.py)：评分程序单元测试。
- [LICENSE-NOTICE.md](LICENSE-NOTICE.md)：数据来源及许可边界。

源数据为 Make Me a Hanzi 固定版本，SHA-256：
`a28c478b5178e98f67f510b2d52fde08a69dc664654ef43498253b9b764d46ee`。
原始 PNG **不提交到 Git 历史中**，以避免在衍生字体素材的再分发条款确认前将其错误视为 MIT 许可；图片由实验分支的 GitHub Actions 基于固定来源重新生成。

## 如何进行自己的视觉模型测试

1. 从实验工作流重新生成 PNG，并按照清单验证哈希。
2. 在所有模型完成回答前，不得让推理端访问目标字符、`ground_truth.csv`、已有回答或研究结果。
3. 按 [PROTOCOL.md](PROTOCOL.md) 的 P1 提示词，对每张图像建立独立、无历史记录的请求。
4. 保留原始响应、不可用状态和错误。冻结响应文件后再运行评分程序：
   `python scripts/score.py --responses data/responses_matrix.csv --key data/ground_truth.csv`。
5. 以“模型×图形”为单位，报告**两个方向均正确**的比例，并报告单方向准确率、与修正基线的配对变化及错误率。

公开答案不意味着模型已遵守盲测；必须通过操作程序确保推理时无法访问答案。未来的留出样本应独立预注册。

## 已知限制

使用的四种模型为 MiniMax M3.1 Flash、DeepSeek V4.1 Flash、Tencent HY4 和 GLM-5.3 Flash。每张 436×436 PNG 在主试验中向每个模型提交一次；温度为 0，输出上限为 4096 token。模型标识是提供商别名，并非带日期锁定的版本。

共记录 **207 次 HTTP 200**、**1 次传输错误**及 **23 次因长度限制而结束的输出**。无效回答、UNKNOWN、错误均按未正确识别处理。统一正式采集前发生过一次较低 token 限额的预试验，已如实记录。

本试验中 A/B 融合对两个配对产生的图像与修正后的简单合并图像逐字节相同，因此不能声称融合产生了效果。自旋转任务的数值提升仍属于小样本描述性发现。

本仓库坚持英语、中文和日语的语言政策；本试验首先提供英语与简体中文材料。原始程序的 MIT 许可**不覆盖**第三方 Arphic 衍生字形素材。
