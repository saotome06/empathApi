#!/bin/bash

# プロジェクトIDとコンテナイメージの変数を設定
_gc_pj_id="rapid-gadget-423315-s1"
_con_img="empathimg"

# gcloudコマンドを実行
sudo gcloud builds submit --tag gcr.io/${_gc_pj_id}/${_con_img} --project ${_gc_pj_id}

