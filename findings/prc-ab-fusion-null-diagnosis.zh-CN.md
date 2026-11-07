# PRC A/B 笔画融合：两组示例无变化的原因

**状态：** 2026 年 11 月 7 日针对原始 CI 产物的独立诊断。实验性 [PR #16](https://github.com/ClaudioDrews/sinogram-ambigram/pull/16) 仍为草稿，未合并、未修改。本结果不属于事先冻结的代表性测试，更不是人类识读实验。

**证据：** [GitHub Actions 运行 42399361826](https://github.com/ClaudioDrews/sinogram-ambigram/actions/runs/42399361826) 中的 `prc-experiment-stimuli` 产物（ID `13584656789`）；实验提交 `c222133c59d07103d162dda5a1a3357764cfd0c7`；来源 SHA-256 `a28c478b5178e98f67f510b2d52fde08a69dc664654ef43498253b9b764d46ee`。四张图像的字节内容已独立比较。

| 字符对 | A 笔画数 | B 笔画数 | 成功匹配的笔画 | 与简单并集不同的图像 |
| --- | ---: | ---: | ---: | ---: |
| 甲 ↔ 由 | 5 | 5 | **0** | **0/2** |
| 韦 ↔ 芈 | 4 | 7 | **0** | **0/2** |

**直接原因：** [PR #16 的 `match_strokes()`](https://github.com/ClaudioDrews/sinogram-ambigram/blob/exp/ab-fusion/code/prc_ab_fusion.py) 使用默认 RMS 中线距离阈值 **4.0**；在这两个示例中均没有找到可匹配的笔画。因此 `construct()` 完全保留未匹配笔画，输出与修正笔画宽度后的 A 加旋转 B 简单并集**逐字节相同**。这不是“融合后被识别模型否定”，而是**融合操作本身没有生效**。

这一结果只解释上述两例。它不能证明其他字符对或其他预先规定阈值的结果，也不能证明人类可读性。后续应先冻结新的非试验样本，再测试最近笔画距离分布、匹配数、实际像素变化、不同阈值和两方向 F1；不得根据这两例事后挑选最有利的阈值。

完整的原始 SHA-256、四张 PNG 的哈希值与可执行复现命令见[英文诊断报告](prc-ab-fusion-null-diagnosis.md)。图像来源受独立 Arphic Public License 约束；此报告不重新发布图像。PR #14–#17 不进行合并或变基。

## 后续独立样本（本报告完成后）

随后在仍未合并的 [PR #21](https://github.com/ClaudioDrews/sinogram-ambigram/pull/21) 中，按预先固定的方案对 32 组新异字配对测试了 RMS 阈值 2、4、8、12、16，另对两组历史示例进行核对。[CI 42415746651](https://github.com/ClaudioDrews/sinogram-ambigram/actions/runs/42415746651) 通过。在阈值 16 时，31/32 组新样本已存在笔画匹配，但最终图形改变的仍为 **0/32**。因此，本报告关于历史阈值 4 的“零匹配”结论仍成立；后续实验另发现**存在匹配但备选融合仍被拒绝**的第二阶段问题。详见[独立实验报告](https://github.com/ClaudioDrews/sinogram-ambigram/blob/exp/ab-fusion-threshold-sensitivity/experiments/ab-fusion-threshold-v1/RESULTS.zh-CN.md)。本补充不修改历史数据或原始结论。
