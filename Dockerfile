# Pythonイメージをベースにする
FROM python:3.9-slim

# ワーキングディレクトリを設定
WORKDIR /app

# 必要なパッケージをインストール
COPY requirements.txt .
RUN pip install -r requirements.txt

# アプリケーションのコードをコピー
COPY . .

# ポート8080を公開
EXPOSE 8080

# アプリケーションを実行
CMD ["python", "main.py"]
