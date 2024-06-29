import requests
from flask import Flask, request, jsonify
import os
import mimetypes
import pydub

app = Flask(__name__)

apikey = os.getenv('EMPATH_API_KEY')
url = os.getenv('EMPATH_URL')

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
    file_path = request.json.get('file_path')
    file_path = convert_to_wav(file_path)
    # ファイルのMIMEタイプを推測
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        mime_type = "application/octet-stream"

    headers = {"ApiKey": apikey}
    files = {"file": (os.path.basename(file_path), open(file_path, "rb"), mime_type)}

    response = requests.post(url, files=files, headers=headers)

    if response.status_code == 200:
        return response.text
    else:
        return response.text, response.status_code

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
