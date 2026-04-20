"""
日程調整ツール - Google Calendar連携版
営業・クライアント対応向けの自動日程調整システム
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.mtls import Credentials as MTLSCredentials
from googleapiclient.discovery import build
import json
import os

# ページ設定
st.set_page_config(
    page_title="日程調整ツール",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# カラーパレット
COLOR_PALETTE = {
    "primary": "#3460FB",
    "primary_dark": "#0017C1",
    "primary_light": "#7096F8",
    "positive": "#197A4B",
    "negative": "#FE3939",
    "gray_dark": "#333333",
    "background": "#F8F8FB",
}

# ページスタイル
st.markdown("""
<style>
    .main {
        background-color: #F8F8FB;
    }
    .stTitle {
        color: #3460FB;
        font-size: 2.5em;
        margin-bottom: 1em;
    }
    .stSubheader {
        color: #0017C1;
        margin-top: 1.5em;
        margin-bottom: 0.5em;
    }
    .availability-box {
        background-color: white;
        border-left: 4px solid #3460FB;
        padding: 1em;
        border-radius: 5px;
        margin: 0.5em 0;
    }
    .selected-time {
        background-color: #D9E6FF;
        border: 2px solid #3460FB;
        padding: 1em;
        border-radius: 5px;
        text-align: center;
        font-size: 1.2em;
        font-weight: bold;
        color: #0017C1;
    }
</style>
""", unsafe_allow_html=True)

# Google Calendar API設定
SCOPES = ['https://www.googleapis.com/auth/calendar']

@st.cache_resource
def get_calendar_service():
    """Google Calendarサービスの初期化"""
    try:
        # サービスアカウントキーのパスを確認
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if credentials_path and os.path.exists(credentials_path):
            credentials = Credentials.from_service_account_file(
                credentials_path, scopes=SCOPES
            )
            return build('calendar', 'v3', credentials=credentials)
    except Exception as e:
        st.warning(f"⚠️ Google Calendar連携の初期化に失敗しました: {str(e)}")
        st.info("セットアップ手順: 環境変数 `GOOGLE_APPLICATION_CREDENTIALS` に認証JSONファイルのパスを設定してください")
        return None

def get_available_slots(service, days_ahead=14, duration_minutes=30, buffer_minutes=15):
    """利用可能な時間帯を取得"""
    if not service:
        return []

    try:
        now = datetime.utcnow()
        available_slots = []

        # 営業時間: 10:00-18:00 (日本時間)
        BUSINESS_START = 10
        BUSINESS_END = 18

        for day_offset in range(1, days_ahead + 1):
            # 土日を除外
            check_date = now + timedelta(days=day_offset)
            if check_date.weekday() >= 5:  # 土日
                continue

            # その日のイベントを取得
            start_of_day = check_date.replace(hour=0, minute=0, second=0)
            end_of_day = start_of_day + timedelta(days=1)

            events_result = service.events().list(
                calendarId='primary',
                timeMin=start_of_day.isoformat() + 'Z',
                timeMax=end_of_day.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            # 予定の時間帯を取得
            busy_times = []
            for event in events:
                if event['status'] != 'cancelled':
                    start = datetime.fromisoformat(
                        event['start'].get('dateTime', event['start'].get('date')).replace('Z', '+00:00')
                    )
                    end = datetime.fromisoformat(
                        event['end'].get('dateTime', event['end'].get('date')).replace('Z', '+00:00')
                    )
                    busy_times.append((start, end))

            # 営業時間内の空き時間を計算
            current_time = check_date.replace(hour=BUSINESS_START, minute=0, second=0)
            end_time = check_date.replace(hour=BUSINESS_END, minute=0, second=0)

            while current_time + timedelta(minutes=duration_minutes) <= end_time:
                slot_end = current_time + timedelta(minutes=duration_minutes)

                # この時間帯が空いているか確認
                is_available = True
                for busy_start, busy_end in busy_times:
                    if not (slot_end <= busy_start or current_time >= busy_end):
                        is_available = False
                        break

                if is_available:
                    available_slots.append({
                        'date': current_time.date(),
                        'start_time': current_time,
                        'end_time': slot_end,
                        'display': f"{current_time.strftime('%Y年%m月%d日 %H:%M')} - {slot_end.strftime('%H:%M')}"
                    })

                current_time += timedelta(minutes=duration_minutes + buffer_minutes)

        return available_slots

    except Exception as e:
        st.error(f"❌ スケジュール取得エラー: {str(e)}")
        return []

def add_event_to_calendar(service, start_time, end_time, visitor_name, visitor_email, meeting_title="打ち合わせ"):
    """カレンダーにイベントを追加"""
    if not service:
        st.error("❌ Google Calendar連携が設定されていません")
        return False

    try:
        event = {
            'summary': f"{meeting_title} - {visitor_name}様",
            'description': f"訪問者: {visitor_name}\nメール: {visitor_email}",
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'Asia/Tokyo'
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'Asia/Tokyo'
            },
            'attendees': [
                {'email': visitor_email}
            ]
        }

        created_event = service.events().insert(
            calendarId='primary',
            body=event,
            sendNotifications=True
        ).execute()

        return True

    except Exception as e:
        st.error(f"❌ イベント追加エラー: {str(e)}")
        return False

# ===== メイン画面 =====

st.markdown("# 📅 日程調整ツール")
st.markdown("お好みの日時をお選びください。確定すると自動的にカレンダーに反映されます。")
st.markdown("---")

# サイドバー: 詳細設定
with st.sidebar:
    st.markdown("### ⚙️ 設定")
    days_ahead = st.slider("提示期間（日数）", min_value=7, max_value=60, value=14, step=7)
    duration_minutes = st.selectbox(
        "面談時間",
        options=[15, 30, 45, 60],
        index=1,
        format_func=lambda x: f"{x}分"
    )
    meeting_title = st.text_input("会議タイプ", value="打ち合わせ", placeholder="例: オンライン相談、訪問営業など")

# Google Calendar連携の確認
service = get_calendar_service()

# メイン入力フォーム
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📋 お客様情報")
    visitor_name = st.text_input(
        "お名前",
        placeholder="山田太郎",
        help="打ち合わせを予約される方のお名前"
    )

with col2:
    visitor_email = st.text_input(
        "メールアドレス",
        placeholder="yamada@example.com",
        help="確認メール送信用のメールアドレス"
    )

st.markdown("---")

# 利用可能な日時を取得
if service:
    with st.spinner("📅 利用可能な日時を確認中..."):
        available_slots = get_available_slots(service, days_ahead=days_ahead, duration_minutes=duration_minutes)
else:
    available_slots = []
    st.warning("⚠️ Google Calendarが連携されていません。\n\n**セットアップが必要です** → 管理者に連絡してください")

# 日時選択
if available_slots:
    st.markdown(f"### 📌 利用可能な日時（全 {len(available_slots)} 件）")

    # 日付でグループ化
    slots_by_date = {}
    for slot in available_slots:
        date_key = slot['date'].strftime('%Y年%m月%d日 (%a)')
        if date_key not in slots_by_date:
            slots_by_date[date_key] = []
        slots_by_date[date_key].append(slot)

    selected_slot = None

    for date_str in sorted(slots_by_date.keys()):
        with st.expander(f"📅 {date_str}", expanded=False):
            slots = slots_by_date[date_str]

            # 複数列で表示
            cols = st.columns(3)
            for idx, slot in enumerate(slots):
                with cols[idx % 3]:
                    if st.button(
                        f"🕐 {slot['start_time'].strftime('%H:%M')}\n-\n{slot['end_time'].strftime('%H:%M')}",
                        key=f"slot_{idx}",
                        use_container_width=True
                    ):
                        selected_slot = slot
                        st.session_state.selected_slot = slot

    # セッション状態から選択を取得
    if 'selected_slot' in st.session_state:
        selected_slot = st.session_state.selected_slot

    # 選択された日時の表示
    if selected_slot:
        st.markdown("---")
        st.markdown("### ✅ ご予約内容")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📅 日付", selected_slot['start_time'].strftime('%Y年%m月%d日'))
        with col2:
            st.metric("🕐 開始時間", selected_slot['start_time'].strftime('%H:%M'))
        with col3:
            st.metric("⏱️ 面談時間", f"{duration_minutes}分")

        st.markdown("---")

        # 確認メッセージ
        if visitor_name and visitor_email:
            st.success(f"✨ {visitor_name}様のご予約を確定します")

            col1, col2 = st.columns([2, 1])

            with col1:
                confirm_text = st.text_area(
                    "📝 備考（オプション）",
                    placeholder="ご不明な点や特にお話しされたいことがあればお知らせください",
                    height=100
                )

            with col2:
                st.markdown("")
                st.markdown("")
                if st.button("✅ 予約確定", use_container_width=True, type="primary"):
                    # イベントを追加
                    success = add_event_to_calendar(
                        service,
                        selected_slot['start_time'],
                        selected_slot['end_time'],
                        visitor_name,
                        visitor_email,
                        meeting_title
                    )

                    if success:
                        st.balloons()
                        st.success(f"🎉 ご予約ありがとうございます！\n\n**{selected_slot['display']}**\n\n確認メールを {visitor_email} にお送りしました。")
                        st.info(f"📧 当日に改めてご連絡させていただきます。ご質問があればお気軽にお問い合わせください。")

                        # リセット
                        if st.button("🔄 別の日時で予約", use_container_width=True):
                            del st.session_state.selected_slot
                            st.rerun()
                    else:
                        st.error("❌ 予約の確定に失敗しました。もう一度お試しください。")
        else:
            st.warning("⚠️ お名前とメールアドレスをご入力ください")
else:
    st.error("❌ 利用可能な日時がありません")
    if not service:
        st.markdown("""
        ### セットアップが必要です

        このツールを使用するには、Google Calendar APIの認証が必要です。

        **管理者向けセットアップ手順:**

        1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
        2. プロジェクトを作成または選択
        3. Calendar API を有効化
        4. サービスアカウントキー (JSON) をダウンロード
        5. 環境変数を設定:
           ```bash
           export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
           ```
        6. Streamlit アプリを再起動:
           ```bash
           streamlit run schedule_coordinator.py
           ```
        """)

# フッター
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666666; font-size: 0.9em;'>
    📞 ご不明な点があれば、お気軽にお問い合わせください<br>
    Made with ❤️ by Scheduling System
</div>
""", unsafe_allow_html=True)
