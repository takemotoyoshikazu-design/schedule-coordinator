# 📅 日程調整ツール - セットアップガイド

このガイドに従い、Google Calendar連携の日程調整ツールをセットアップします。

---

## 📋 目次

1. [前提条件](#前提条件)
2. [Google Cloud設定](#google-cloud設定)
3. [ローカルインストール](#ローカルインストール)
4. [デプロイ方法](#デプロイ方法)
5. [使用方法](#使用方法)
6. [トラブルシューティング](#トラブルシューティング)

---

## 前提条件

- Python 3.8以上
- Google アカウント（営業担当者の個人アカウント）
- インターネット接続

---

## Google Cloud設定

### ステップ1: プロジェクトを作成

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 上部の「プロジェクト選択」→「新しいプロジェクト」をクリック
3. プロジェクト名を入力（例：`Schedule-Coordinator`）
4. 「作成」をクリック

### ステップ2: Calendar APIを有効化

1. Cloud Consoleでプロジェクトを選択
2. 左メニューから「API とサービス」→「ライブラリ」をクリック
3. 検索バーで「Google Calendar API」を検索
4. クリックして「有効化」をクリック

### ステップ3: サービスアカウントを作成

1. 「API とサービス」→「認証情報」をクリック
2. 「認証情報を作成」→「サービスアカウント」をクリック
3. サービスアカウント名を入力（例：`schedule-api`）
4. 「作成と続行」をクリック
5. ロールは**Editor**を選択（フルアクセスが必要）
6. 「続行」→「完了」をクリック

### ステップ4: 認証キーをダウンロード

1. 作成したサービスアカウントをクリック
2. 「キー」タブを開く
3. 「キーを追加」→「新しいキーを作成」
4. **JSON** 形式を選択して「作成」
5. JSONファイルが自動ダウンロードされます（`service-account-key.json`）

### ステップ5: Google Calendarでサービスアカウントを許可

1. [Google Calendar](https://calendar.google.com/) を開く
2. 左メニューの「設定」→「設定」をクリック
3. 左メニューから「カレンダーを追加」→「カレンダーを登録する」
4. ダウンロードしたJSONファイルから `client_email` をコピー
5. そのメールアドレスをカレンダーの共有相手に追加（編集権限）

**JSONファイルから client_email を確認する方法:**

```bash
cat service-account-key.json | grep "client_email"
```

出力例: `"client_email": "schedule-api@project-id.iam.gserviceaccount.com"`

---

## ローカルインストール

### ステップ1: 必要なパッケージをインストール

```bash
pip install -r requirements.txt
```

### ステップ2: 環境変数を設定

JSONファイルのパスを環境変数に登録します。

**macOS / Linux:**

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

**Windows (PowerShell):**

```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\service-account-key.json"
```

永続的に設定する場合は、`.bashrc` や `.zshrc` に追加してください。

### ステップ3: ローカルで実行

```bash
streamlit run schedule_coordinator.py
```

ブラウザが自動的に開き、`http://localhost:8501` が表示されます。

---

## デプロイ方法

### 方法1: Streamlit Cloud（推奨・無料）

Streamlit CloudでURLを自動生成・管理できます。

#### 1. リポジトリをGitHubにプッシュ

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/schedule-coordinator.git
git push -u origin main
```

#### 2. Streamlit Cloudにデプロイ

1. [Streamlit Cloud](https://streamlit.io/cloud) にアクセス
2. GitHubアカウントでサインイン
3. 「New app」をクリック
4. リポジトリを選択: `schedule-coordinator`
5. メインファイル: `schedule_coordinator.py`
6. 「Deploy」をクリック

#### 3. シークレットを設定

1. デプロイされたアプリの右上「≡」→「Settings」
2. 「Secrets」をクリック
3. JSONファイルの内容をコピー＆ペースト

#### 4. 公開URLを取得

デプロイ完了後、自動生成されたURLが表示されます。

**例:** `https://schedule-coordinator.streamlit.app/`

### 方法2: Heroku（有料・カスタマイズ可能）

```bash
heroku login
heroku create schedule-coordinator
git push heroku main
```

### 方法3: AWS / Google Cloud Run

設定ファイルを別途提供します。お問い合わせください。

---

## 使用方法

### クライアント（訪問者）向け

1. 公開URLにアクセス
2. お名前とメールアドレスを入力
3. 利用可能な日時から選択
4. 「予約確定」をクリック
5. 確認メールが送信されます

### 営業担当者（あなた）向け

- Google Calendar が自動的に更新されます
- 「打ち合わせ - [顧客名]」という予定が追加されます
- 訪問者にカレンダー招待が送信されます

---

## カスタマイズ

### 営業時間を変更

`schedule_coordinator.py` の以下の部分を編集:

```python
BUSINESS_START = 10  # 開始時間 (デフォルト: 10:00)
BUSINESS_END = 18    # 終了時間 (デフォルト: 18:00)
```

### 土日を営業日に設定

```python
if check_date.weekday() >= 5:  # 0=月, 5=土, 6=日
    continue
```

このコードを削除するか、条件を変更します。

### デフォルト提示期間を変更

```python
days_ahead = st.slider("提示期間（日数）", min_value=7, max_value=60, value=30, step=7)
```

`value=30` をお好みの日数に変更。

---

## トラブルシューティング

### ❌ "Google Calendar連携が設定されていません"

**原因:** 環境変数が正しく設定されていない

**解決策:**
```bash
# 環境変数を確認
echo $GOOGLE_APPLICATION_CREDENTIALS

# 設定されていなければ、再度設定
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"

# アプリを再起動
streamlit run schedule_coordinator.py
```

### ❌ "Permission denied" エラー

**原因:** サービスアカウントがカレンダーへのアクセス権を持っていない

**解決策:**
1. Google Calendarの設定で、サービスアカウントのメールアドレスを共有相手に追加
2. **編集権限**を付与

### ❌ "利用可能な日時がありません"

**原因:** 提示期間内にスケジュール空きがない

**解決策:**
- カレンダーの予定を確認
- 営業時間外になっていないか確認
- 提示期間を広げる

### ❌ イベント追加後、メール通知が来ない

**原因:** Google Calendar の通知設定

**解決策:**
1. Google Calendar の「設定」→「通知」を確認
2. メール通知をオン
3. または、コード内の `sendNotifications=False` → `True` に変更

---

## セキュリティに関する注意

⚠️ **重要:**

- `service-account-key.json` を **GitHub に push しない**
- `.gitignore` に追加:
  ```
  service-account-key.json
  .env
  *.json
  ```
- Streamlit Cloud使用時は「Secrets」機能でJSONを管理（ファイルではなく文字列）

---

## サポート

ご不明な点や問題が発生した場合は、お気軽にお問い合わせください。

**よくある質問:**
- **複数の営業担当者が使いたい** → カレンダーごとに別アプリをデプロイ
- **複数のメールアドレスで予約を受け付けたい** → コードをカスタマイズ
- **Zoomリンクを自動挿入したい** → 事前に用意したZoomURLをイベント説明に追加可能

---

**最終更新:** 2026年4月

Made with ❤️ by Scheduling System
