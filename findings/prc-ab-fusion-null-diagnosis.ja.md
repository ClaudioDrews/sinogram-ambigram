# PRC 異字 A/B 融合：二組の例で結果が変化しなかった原因

**状態：** 2026年11月7日に元の CI 成果物を調べた独立した診断。[PR #16](https://github.com/ClaudioDrews/sinogram-ambigram/pull/16) は未統合のドラフトであり、ブランチは変更していない。この二組は事前に独立抽出した検証標本ではない。

**再現資料：** [GitHub Actions 実行 42399361826](https://github.com/ClaudioDrews/sinogram-ambigram/actions/runs/42399361826)、成果物 `prc-experiment-stimuli`（ID `13584656789`）、実験コミット `c222133c59d07103d162dda5a1a3357764cfd0c7`。元データの SHA-256 は `a28c478b5178e98f67f510b2d52fde08a69dc664654ef43498253b9b764d46ee`。

| 文字の組 | A の画数 | B の画数 | 対応した画数 | 単純な重ね合わせから変化した画像 |
| --- | ---: | ---: | ---: | ---: |
| 甲 ↔ 由 | 5 | 5 | **0** | **0/2** |
| 韦 ↔ 芈 | 4 | 7 | **0** | **0/2** |

**直接の原因：** [PR #16 の `match_strokes()`](https://github.com/ClaudioDrews/sinogram-ambigram/blob/exp/ab-fusion/code/prc_ab_fusion.py) は、再標本化した画の中心線について RMS 距離 **4.0** を既定の対応判定閾値としている。今回の二組では、対応が一つも得られなかった。そのため `construct()` は全画を未対応のまま保持し、A と180度回転した B の単純な重ね合わせと**全4枚の PNG がバイト単位で一致**した。したがって、融合の有効性が否定されたのではなく、**融合操作が発動していない**。

この結果を別の文字や閾値、人間の読字可能性へ一般化してはならない。次の段階では、既存の二組を除いた独立標本を先に固定し、最近傍の中心線距離、対応数、実際に変わった画素、両方向の F1 を閾値別に記録する必要がある。元の画像ハッシュと再現手順は[英語版の報告](prc-ab-fusion-null-diagnosis.md)を参照。

文字画像は Make Me a Hanzi 由来であり、コードの MIT ライセンスとは異なる Arphic Public License に従う。PR #14–#17 のマージやリベースは行わない。

## 本報告後に実施した独立標本の追試

[未統合の PR #21](https://github.com/ClaudioDrews/sinogram-ambigram/pull/21) では、事前に固定した新規異字ペア32組と従来の確認用2組を使い、RMS閾値2、4、8、12、16を比較した。[CI 42415746651](https://github.com/ClaudioDrews/sinogram-ambigram/actions/runs/42415746651) は成功した。閾値16では新規ペア31/32組で筆画の対応付けが生じたものの、最終的に画素が変化したペアは **0/32** 組だった。よって、本報告の閾値4における「対応付けなし」という歴史的診断は引き続き正しい。一方、追試では**対応付け後に候補が採択されない第二の問題**が明らかになった。詳細は[追試結果](https://github.com/ClaudioDrews/sinogram-ambigram/blob/exp/ab-fusion-threshold-sensitivity/experiments/ab-fusion-threshold-v1/RESULTS.ja.md)。ここでは過去のデータと結論を変更しない。
