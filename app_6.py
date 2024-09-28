import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import pulp
import streamlit as st

from src.ShiftScheduler import ShiftScheduler

import matplotlib.pyplot as plt


# タイトル
st.title("シフトスケジューリングアプリ")

# サイドバー
st.sidebar.header("データのアップロード")
# calendar_file = st.sidebar.file_uploader("カレンダー", type=["csv"])
# staff_file = st.sidebar.file_uploader("スタッフ", type=["csv"])

calendar_file = "data/calendar.csv"
staff_file = "data/staff.csv"


# タブ
tab1, tab2, tab3 = st.tabs(["カレンダー情報", "スタッフ情報", "シフト表作成"])

with tab1:
    if calendar_file is None:
        st.write("カレンダー情報をアップロードしてください")
    else:
        st.markdown("## カレンダー情報")
        calendar_data = pd.read_csv(calendar_file)
        st.table(calendar_data)

with tab2:
    if staff_file is None:
        st.write("スタッフ情報をアップロードしてください")
    else:
        st.markdown("## スタッフ情報")
        staff_data = pd.read_csv(staff_file)
        st.table(staff_data)

with tab3:
    if staff_file is None:
        st.write("スタッフ情報をアップロードしてください")
    if calendar_file is None:
        st.write("カレンダー情報をアップロードしてください")
    if staff_file is not None and calendar_file is not None:
        optimize_button = st.button("最適化実行")
        if optimize_button:
            # ShiftSchedulerクラスのインスタンスを作成
            shift_scheduler = ShiftScheduler()
            # データをセット
            shift_scheduler.set_data(staff_data, calendar_data)
            # モデルを構築
            shift_scheduler.build_model()
            # 最適化を実行
            shift_scheduler.solve()

            st.markdown("## 最適化結果")

            # 最適化結果の出力
            st.write("実行ステータス:", pulp.LpStatus[shift_scheduler.status])
            st.write("目的関数値:", pulp.value(shift_scheduler.model.objective))

            
            st.markdown("## シフト表")
            st.table(shift_scheduler.sch_df)
        
            st.markdown("## シフト数の充足確認")
            # 各スタッフの合計シフト数をstreanlitのbar chartで表示
            # sum(axis=0で列に関して合計をとる)
            shift_sum = shift_scheduler.sch_df.sum(axis=0)
            st.bar_chart(shift_sum)
            
            st.markdown("## スタッフの希望の確認")
            # sum(axis=1で列に関して合計をとる)
            staff_sum = shift_scheduler.sch_df.sum(axis=1)
            st.bar_chart(staff_sum)

            
            st.markdown("## 責任者の合計シフト数の充足確認")
            # shift_scheduleに対してstaff_dataをマージして責任者の合計シフト数を計算
            shift_schedule_with_staff_data = pd.merge(
                shift_scheduler.sch_df,
                staff_data,
                left_index=True,
                right_on="スタッフID",
            )
            # 責任者フラグが1の行のみqueryで抽出
            shift_chief_only = shift_schedule_with_staff_data.query("責任者フラグ == 1")
            # 不要な列はdropで削除する
            shift_chief_only = shift_chief_only.drop(
                columns=[
                    "スタッフID",
                    "責任者フラグ",
                    "希望最小出勤日数",
                    "希望最大出勤日数",
                ]
            )
            shift_chief_sum = shift_chief_only.sum(axis=0)
            st.bar_chart(shift_chief_sum)

            シフト表のダウンロード
            st.download_button(
                label="シフト表をダウンロード",
                data=shift_scheduler.sch_df.to_csv().encode("utf-8-sig"),
                file_name="output.csv",
                mime="text/csv",
            )

            # # シフト表をCVS形式に変換
            # shift_csv = shift_scheduler.sch_df.to_csv(index=True, encoding='utf-8-sig')

            # # ダウンロードボタンを作成
            # st.download_button(
            #     label="シフト表をダウンロード",
            #     data=shift_csv,
            #     file_name="shift_schedule.csv",
            #     mime="text/csv",
            # )
            # シフト表のダウンロード
            # csv = shift_scheduler.sch_df.to_csv(index=False)
            # b64 = base64.b64encode(csv.encode("utf-8-sig")).decode()
            # href = f'<a href="data:application/octet-stream;base64,{b64}" download="output.csv">CSVファイルのダウンロード</a>'
            # st.markdown(f"{href}", unsafe_allow_html=True)
