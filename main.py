import requests
from flask import Flask, request, jsonify
import os
import mimetypes
import pydub

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def convert_to_wav(file_path):
    # ファイルの拡張子を取得
    extension = os.path.splitext(file_path)[1][1:]

    # PyDubを使用してオーディオファイルを読み込む
    audio = pydub.AudioSegment.from_file(file_path, format=extension)

    # 新しいファイルパスを生成
    wav_file_path = file_path.rsplit(".", 1)[0] + ".wav"

    # WAV形式でファイルを保存
    audio.export(wav_file_path, format="wav")

    return wav_file_path
@app.route('/run-script', methods=['POST'])
def upload_file_to_chunk_endpoint():
    apikey = os.getenv('EMPATH_API_KEY')
    if apikey is None:
        raise ValueError('EMPATH_API_KEY is not set')
    url = os.getenv('EMPATH_URL')
    try:
        # ファイルデータを受け取る
        file_data = request.data

        # サーバー上に保存するためのパス
        save_path = os.path.join("uploads", "received_audio.wav")
        with open(save_path, "wb") as dest_file:
            dest_file.write(file_data)

        wav_file_path = convert_to_wav(save_path)

        # ファイルのMIMEタイプを推測
        mime_type = "audio/wav"  # 例としてwav形式を指定

        headers = {"ApiKey": apikey}  # 必要に応じてAPIキーを設定
        files = {"file": (os.path.basename(wav_file_path), open(wav_file_path, "rb"), mime_type)}

        # リクエストを送信
        response = requests.post(url, files=files, headers=headers)

        if response.status_code == 200:
            return response.text
        else:
            return response.text, response.status_code

    except Exception as e:
        return jsonify({"error": f"Error processing file: {str(e)}"}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
