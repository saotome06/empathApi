from supabase import create_client, Client
import requests
from flask import Flask, request, jsonify
import os
import mimetypes
import pydub
import json
from datetime import datetime
import pytz

app = Flask(__name__)

SUPABASE_KEY=os.getenv('SUPABASE_KEY')
SUPABASE_URL=os.getenv('SUPABASE_URL')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def extract_emotion(response_text):
    # レスポンスをJSONオブジェクトに変換
    response_json = json.loads(response_text)

    # "talkUnits" の各要素から "emotion" を抽出
    emotions = [unit["emotion"] for unit in response_json["talkUnits"]]

    return emotions[0]

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

def update_empath_result(emotions, user_email):
    # タイムスタンプを取得する
    utc_now = datetime.utcnow()
    jst_now = utc_now.astimezone(pytz.timezone('Asia/Tokyo'))
    timestamp = jst_now.isoformat()
    
    # emotionsにタイムスタンプを追加する
    emotions_with_timestamp = {**emotions, "timestamp": timestamp}

    # ユーザーの現在の感情データを取得する
    empath_result_log_response = (
        supabase.table("users")
        .select("empath_result_log")
        .eq("user_email", user_email)
        .execute()
    )
    current_emotions = empath_result_log_response.data[0]['empath_result_log']
    if current_emotions is None:
        current_emotions = []
    # 現在の感情データに新しい感情データを追加する
    current_emotions.append(emotions_with_timestamp)
    # レコードを更新する
    response = (
        supabase.table("users")
        .update({"empath_result_log": current_emotions})
        .eq("user_email", user_email)
        .execute()
    )
    # empath_response = (
    #     supabase.table("users")
    #     .update({"empath_response": emotions})
    #     .eq("user_email", user_email)
    #     .execute()
    # )
    return response

@app.route('/run-script', methods=['POST'])
def upload_file_to_chunk_endpoint():
    apikey = os.getenv('EMPATH_API_KEY')
    if apikey is None:
        raise ValueError('EMPATH_API_KEY is not set')
    url = os.getenv('EMPATH_URL')
    try:
        # ファイルデータを受け取る
        user_email = request.form.get('email')
        file = request.files['file']
        file_data = file.read()
        # file_data = request.data

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
        emotions = extract_emotion(response.text)
        update_empath_result(emotions, user_email)

        if response.status_code == 200:
            return response.text
        else:
            return response.text, response.status_code

    except Exception as e:
        return jsonify({"error": f"Error processing file: {str(e)}"}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
