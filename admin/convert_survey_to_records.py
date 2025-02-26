# アンケートの集計用スクリプト

import pandas as pd

# CSVファイルを読み込む
df = pd.read_csv('input.csv', delimiter='\t')

# ヘッダーから回答者リストを取得
# 最初の3列（質問の大分類、質問の分類、質問内容）を除いた列名が回答者
respondents = df.columns[3:].tolist()
print(respondents)