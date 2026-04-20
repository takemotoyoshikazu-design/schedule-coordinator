# 📅 日程調整ツール（Google Calendar連携版）

営業・クライアント対応向けの**自動日程調整システム**です。URLを共有するだけで、訪問者が自由に予約できます。

## 🎯 特徴

✅ **自動スケジュール取得** - Google Calendarから空き時間を自動抽出  
✅ **ワンクリック予約** - 訪問者が複数の候補から選択して確定  
✅ **自動カレンダー追加** - 確定と同時に自分のカレンダーに反映  
✅ **自動メール通知** - 訪問者に確認メールを送信  
✅ **営業時間設定** - 営業時間外は提示しない  
✅ **土日除外** - デフォルトで平日のみ提示  
✅ **バッファ時間設定** - 面談間の移動時間を自動確保  

## 🚀 5分でスタート

### 1. パッケージをインストール

```bash
pip install -r requirements.txt
```

### 2. Google Cloud設定（初回のみ）

[SETUP_GUIDE.md](./SETUP_GUIDE.md) の「Google Cloud設定」セクションに従って設定してください。  
ダウンロードしたJSONファイルのパスを環境変数に設定:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

### 3. アプリを起動

```bash
streamlit run schedule_coordinator.py
```

**出力例:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

ブラウザで `http://localhost:8501` を開くと、アプリが表示されます。

---

## 🌐 URLを公開する（無料）

### Streamlit Cloud で自動デプロイ（最も簡単）

1. GitHubにコードをプッシュ
2. [Streamlit Cloud](https://streamlit.io/cloud) にサインイン
3. 「New app」→ リポジトリ選択 → 「Deploy」

**自動生成URL例:** `https://schedule-coordinator.streamlit.app/`

📌 詳細は [SETUP_GUIDE.md](./SETUP_GUIDE.md) の「デプロイ方法」をご参照ください。

---

## 📊 使用例

### 訪問者の流れ

```
1. URLを受け取る（メール、SNS、名刺に記載など）
   ↓
2. URLにアクセス
   ↓
3. お名前・メールアドレスを入力
   ↓
4. 利用可能な日時から選択
   ↓
5. 「予約確定」ボタンをクリック
   ↓
6. 確認メールが届く ✅
   ↓
7. あなたのGoogle Calendarに自動追加 ✅
```

### 営業担当者（あなた）の流れ

```
訪問者が予約確定
  ↓
Google Calendar に「打ち合わせ - [顧客名]」が追加される
  ↓
訪問者にメール招待が送信される
  ↓
（オプション）前日に通知を受け取る
```

---

## ⚙️ カスタマイズ例

### 営業時間を 9:00-17:00 に変更

`schedule_coordinator.py` の10行目付近:

```python
BUSINESS_START = 9   # 開始時間
BUSINESS_END = 17    # 終了時間
```

### 面談時間を 60分 に変更

サイドバーの「面談時間」で変更、または コードのデフォルト値を修正:

```python
duration_minutes = st.selectbox(
    "面談時間",
    options=[30, 60],  # 30分と60分のみ表示
    index=1,
    format_func=lambda x: f"{x}分"
)
```

### 複数名で運用する

各営業担当者ごとに別アプリをデプロイ:

```
schedule-coordinator-yamada.streamlit.app
schedule-coordinator-suzuki.streamlit.app
```

コードのコピーと Google Cloud プロジェクトを分けるだけです。

---

## 📁 ファイル構成

```
schedule-coordinator/
├── schedule_coordinator.py    # メインアプリ
├── requirements.txt           # パッケージ一覧
├── SETUP_GUIDE.md            # 詳細セットアップガイド
├── README.md                 # このファイル
├── .gitignore               # Git除外設定
└── service-account-key.json  # ⚠️ 秘密鍵（Gitに push しない）
```

---

## 🔒 セキュリティ

⚠️ **重要な注意:**

- `service-account-key.json` を **GitHub に push しない**
- Streamlit Cloud 使用時は「Secrets」機能を使う（詳細は SETUP_GUIDE.md）
- 定期的にサービスアカウントを確認

---

## 🐛 トラブルシューティング

| 問題 | 解決策 |
|------|------|
| "Google Calendar連携が設定されていません" | 環境変数を確認: `echo $GOOGLE_APPLICATION_CREDENTIALS` |
| "Permission denied" エラー | Google Calendar でサービスアカウントを編集権限で共有 |
| "利用可能な日時がありません" | カレンダーの予定を確認、提示期間を広げる |
| イベント追加後、メール通知が来ない | Google Calendar の通知設定を確認 |

📖 詳細は [SETUP_GUIDE.md](./SETUP_GUIDE.md) の「トラブルシューティング」をご参照ください。

---

## 📞 サポート

ご質問やカスタマイズリクエストがあれば、お気軽にお問い合わせください。

**よくある要望:**
- ✅ Zoom/Teams リンクの自動挿入
- ✅ SMS通知
- ✅ カレンダー言語の変更
- ✅ 複数言語対応
- ✅ 決済機能の連携

---

## 📋 チェックリスト（セットアップ完了確認）

- [ ] Python 3.8以上がインストール済み
- [ ] `pip install -r requirements.txt` を実行済み
- [ ] Google Cloud プロジェクトを作成済み
- [ ] Calendar API を有効化済み
- [ ] サービスアカウント認証キー（JSON）をダウンロード済み
- [ ] 環境変数 `GOOGLE_APPLICATION_CREDENTIALS` を設定済み
- [ ] `streamlit run schedule_coordinator.py` でローカル実行確認済み
- [ ] Streamlit Cloud (またはその他) にデプロイ済み
- [ ] 公開URLにアクセスして動作確認済み

---

## 📚 参考リンク

- [Google Calendar API 公式ドキュメント](https://developers.google.com/calendar)
- [Streamlit 公式ドキュメント](https://docs.streamlit.io/)
- [Streamlit Cloud デプロイガイド](https://docs.streamlit.io/streamlit-cloud/get-started)

---

**最終更新:** 2026年4月  
**バージョン:** 1.0.0

Made with ❤️ by Scheduling System
