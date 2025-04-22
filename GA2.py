import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="فلترة وتحليل بيانات المشاريع العقارية", layout="wide")
st.title("📊 نظام فلترة وتحليل المشاريع العقارية")

# تحميل البيانات
@st.cache_data
def load_data():
    df = pd.read_excel("FF_modified.xlsx")
    base_cols = ['Code', 'Developer name']
    project_sets = [
        ('Project', 'Area', 'Deliver Date'),
        ('Project 2', 'Area.1', 'Deliver Date.1'),
        ('Project 3', 'Area.2', 'Deliver Date.2'),
        ('Project 4', 'Area.3', 'Deliver Date.3'),
        ('Project 5', 'Area.4', 'Deliver Date.4')
    ]

    all_parts = []
    for project_col, area_col, date_col in project_sets:
        temp = df[base_cols + [project_col, area_col, date_col]].copy()
        temp.columns = ['Code', 'Developer', 'Project', 'Area', 'Deliver Date']
        all_parts.append(temp)

    long_df = pd.concat(all_parts, ignore_index=True)
    long_df = long_df.dropna(subset=['Project'])
    long_df.reset_index(drop=True, inplace=True)
    return long_df

# تحميل البيانات
projects_df = load_data()

# الشريط الجانبي للفلاتر
st.sidebar.header("🔍 فلترة متقدمة")

with st.sidebar.expander("تحديد الفلاتر"):
    all_devs = sorted(projects_df['Developer'].dropna().unique())
    all_areas = sorted(projects_df['Area'].dropna().unique())
    all_dates = sorted(projects_df['Deliver Date'].dropna().astype(str).unique())

    col1, col2 = st.columns(2)
    with col1:
        developers = st.multiselect("اختر المطورين:", options=all_devs, default=None, placeholder="كل المطورين")
    with col2:
        areas = st.multiselect("اختر المناطق:", options=all_areas, default=None, placeholder="كل المناطق")

    deliver_dates = st.multiselect("اختر تواريخ التسليم:", options=all_dates, default=None, placeholder="كل التواريخ")

    apply_filters = st.button("🔎 تنفيذ الفلترة")

# تطبيق الفلاتر فقط عند الضغط على زر الفلترة
if apply_filters:
    filtered_df = projects_df.copy()

    if developers:
        filtered_df = filtered_df[filtered_df['Developer'].isin(developers)]
    if areas:
        filtered_df = filtered_df[filtered_df['Area'].isin(areas)]
    if deliver_dates:
        filtered_df = filtered_df[filtered_df['Deliver Date'].astype(str).isin(deliver_dates)]

    st.markdown(f"### 🏗️ عدد المشاريع بعد الفلترة: {len(filtered_df)}")
    st.dataframe(filtered_df, use_container_width=True)

    # زر تحميل النتائج
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        filtered_df.to_excel(writer, index=False)
    output.seek(0)

    st.download_button(
        label="📥 تحميل النتائج كملف Excel",
        data=output,
        file_name="Filtered_Projects.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("يرجى اختيار الفلاتر المطلوبة من القائمة الجانبية ثم الضغط على \"تنفيذ الفلترة\"")