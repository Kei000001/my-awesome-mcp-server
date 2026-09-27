# ユーティリティ関数集

def calculate_area(width, height):
    """長方形の面積を計算する"""
    # 幅と高さを掛け算
    return width * height

def format_price(price):
    """価格を通貨形式にフォーマット"""
    # 3桁ごとにカンマを入れて円記号を付ける
    return f"¥{price:,}"

# メイン処理
if __name__ == "__main__":
    # テスト実行
    print(calculate_area(10, 20))
