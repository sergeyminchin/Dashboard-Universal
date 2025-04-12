
import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import io

# Load and display logo
logo = Image.open("logo.png")
st.image(logo, use_container_width=False)

# Sidebar: Upload Excel files
st.sidebar.header("Upload Excel Files")
file_1 = st.sidebar.file_uploader("Upload First File (e.g. Q1 2024)", type=["xlsx"], key="file1")
file_2 = st.sidebar.file_uploader("Upload Second File (e.g. Q1 2025)", type=["xlsx"], key="file2")

if file_1 and file_2:
    # Get user input for labeling
    label_1 = st.sidebar.text_input("Label for First File", value="Dataset 1")
    label_2 = st.sidebar.text_input("Label for Second File", value="Dataset 2")

    # Load all sheets
    total_1 = pd.read_excel(file_1, sheet_name='כמות קריאות').iloc[0, 0]
    total_2 = pd.read_excel(file_2, sheet_name='כמות קריאות').iloc[0, 0]

    total_calls_summary = pd.DataFrame({
        'Period': [label_1, label_2],
        'Total Calls': [total_1, total_2]
    })
    total_calls_summary['Change (%)'] = total_calls_summary['Total Calls'].pct_change().round(2) * 100

    repeated_1 = pd.read_excel(file_1, sheet_name='קריאות חוזרות לפי טכנאי').assign(Period=label_1)
    repeated_2 = pd.read_excel(file_2, sheet_name='קריאות חוזרות לפי טכנאי').assign(Period=label_2)
    combined_repeated = pd.concat([repeated_1, repeated_2])

    perf_1 = repeated_1[['טכנאי', 'קריאות חוזרות', 'סה"כ ביקורים']].copy()
    perf_1['אחוז חוזרות'] = (perf_1['קריאות חוזרות'] / perf_1['סה"כ ביקורים'] * 100).round(2)
    perf_1['Period'] = label_1

    perf_2 = repeated_2[['טכנאי', 'קריאות חוזרות', 'סה"כ ביקורים']].copy()
    perf_2['אחוז חוזרות'] = (perf_2['קריאות חוזרות'] / perf_2['סה"כ ביקורים'] * 100).round(2)
    perf_2['Period'] = label_2

    technician_performance = pd.concat([perf_1, perf_2])

    by_type_1 = pd.read_excel(file_1, sheet_name='התפלגות סוגי קריאה', index_col=0).reset_index().assign(Period=label_1)
    by_type_2 = pd.read_excel(file_2, sheet_name='התפלגות סוגי קריאה', index_col=0).reset_index().assign(Period=label_2)
    calls_by_type = pd.concat([by_type_1, by_type_2])
    calls_by_type.rename(columns={calls_by_type.columns[0]: 'סוג קריאה'}, inplace=True)

    parts_1 = pd.read_excel(file_1, sheet_name='חלקים הכי נפוצים').assign(Period=label_1)
    parts_2 = pd.read_excel(file_2, sheet_name='חלקים הכי נפוצים').assign(Period=label_2)
    combined_parts = pd.concat([parts_1, parts_2])

    faults_1 = pd.read_excel(file_1, sheet_name='תקלות לפי דגם').assign(Period=label_1)
    faults_2 = pd.read_excel(file_2, sheet_name='תקלות לפי דגם').assign(Period=label_2)
    combined_faults = pd.concat([faults_1, faults_2])

    site_1 = pd.read_excel(file_1, sheet_name='קריאות לפי אתר').assign(Period=label_1)
    site_2 = pd.read_excel(file_2, sheet_name='קריאות לפי אתר').assign(Period=label_2)
    combined_sites = pd.concat([site_1, site_2])

    visits_1 = pd.read_excel(file_1, sheet_name='ביקורים טכניים לפי דגם').assign(Period=label_1)
    visits_2 = pd.read_excel(file_2, sheet_name='ביקורים טכניים לפי דגם').assign(Period=label_2)
    combined_visits = pd.concat([visits_1, visits_2])

    calls_by_tech_1 = pd.read_excel(file_1, sheet_name='קריאות לפי טכנאי וסוג קריאה').assign(Period=label_1)
    calls_by_tech_2 = pd.read_excel(file_2, sheet_name='קריאות לפי טכנאי וסוג קריאה').assign(Period=label_2)
    combined_calls_by_tech = pd.concat([calls_by_tech_1, calls_by_tech_2])
    combined_calls_by_tech['סוג קריאה'] = combined_calls_by_tech['סוג קריאה'].replace('תחזוקה', 'תחזוקה/שיפוץ/בדיקה')

    # Colors
    polytex_colors = ['#f46c04', '#003B70']

    # Dashboard sections
    st.title(f"Service Calls Comparison Dashboard: {label_1} vs {label_2}")

    st.subheader('Overall Calls Summary')
    st.dataframe(total_calls_summary)
    st.plotly_chart(px.bar(total_calls_summary, x='Period', y='Total Calls', color='Period',
                           text='Total Calls', title='Total Calls Comparison',
                           color_discrete_sequence=polytex_colors))

    st.subheader('Technician Performance Summary')
    st.dataframe(technician_performance)

    st.subheader('Repeated Calls by Technician')
    tech = st.selectbox('Technician Filter', ['All'] + combined_repeated['טכנאי'].unique().tolist())
    rep_filtered = combined_repeated if tech == 'All' else combined_repeated[combined_repeated['טכנאי'] == tech]
    st.plotly_chart(px.bar(rep_filtered, x='טכנאי', y='קריאות חוזרות', color='Period',
                           title='Repeated Calls by Technician',
                           barmode='group', color_discrete_sequence=polytex_colors))

    st.subheader('Service Calls by Type')
    selected_type = st.selectbox('Call Type', ['All'] + calls_by_type['סוג קריאה'].unique().tolist())
    filtered_type = calls_by_type if selected_type == 'All' else calls_by_type[calls_by_type['סוג קריאה'] == selected_type]
    st.plotly_chart(px.bar(filtered_type, x='סוג קריאה', y='count', color='Period',
                           barmode='group', title='Calls by Type',
                           color_discrete_sequence=polytex_colors))

    st.subheader('Parts Usage')
    part_column = combined_parts.columns[0]
    part = st.selectbox('Part Name', ['All'] + combined_parts[part_column].unique().tolist())
    filtered_parts = combined_parts
    if part != 'All':
        filtered_parts = combined_parts[combined_parts[part_column] == part]
    st.plotly_chart(px.bar(filtered_parts, x=filtered_parts.columns[0], y=filtered_parts.columns[1], color='Period',
                           barmode='group', title='Most Used Parts',
                           color_discrete_sequence=polytex_colors))

    st.subheader('Most Common Faults')
    fault = st.selectbox('Select Fault', ['All'] + faults_1[faults_1.columns[0]].unique().tolist())
    fault_filtered = combined_faults if fault == 'All' else combined_faults[combined_faults[faults_1.columns[0]] == fault]
    st.plotly_chart(px.bar(fault_filtered, x=faults_1.columns[0], y=faults_1.columns[1], color='Period',
                           barmode='group', title='Common Faults by Model',
                           color_discrete_sequence=polytex_colors))

    st.subheader('Service Calls by Site')
    site = st.selectbox('Select Site', ['All'] + site_1[site_1.columns[0]].unique().tolist())
    site_filtered = combined_sites if site == 'All' else combined_sites[combined_sites[site_1.columns[0]] == site]
    st.plotly_chart(px.bar(site_filtered, x=site_1.columns[0], y=site_1.columns[1], color='Period',
                           barmode='group', title='Calls by Site',
                           color_discrete_sequence=polytex_colors))

    st.subheader('Technical Visits by Model')
    model = st.selectbox('Select Model', ['All'] + visits_1[visits_1.columns[0]].unique().tolist())
    model_filtered = combined_visits if model == 'All' else combined_visits[combined_visits[visits_1.columns[0]] == model]
    st.plotly_chart(px.bar(model_filtered, x=visits_1.columns[0], y=visits_1.columns[1], color='Period',
                           barmode='group', title='Visits by Model',
                           color_discrete_sequence=polytex_colors))

    st.subheader('Call Types per Technician')
    call_type = st.selectbox('Call Type Filter', ['All'] + combined_calls_by_tech['סוג קריאה'].unique().tolist())
    filtered_calls = combined_calls_by_tech if call_type == 'All' else combined_calls_by_tech[combined_calls_by_tech['סוג קריאה'] == call_type]
    st.plotly_chart(px.bar(filtered_calls, x='לטיפול', y='כמות קריאות', color='Period',
                           barmode='group', title='Call Types per Technician',
                           color_discrete_sequence=polytex_colors))
else:
    st.warning("Please upload both Excel files to begin analysis.")
