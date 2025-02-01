import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout='wide')

def std_to_quarter(row, col_name):
    """Categorizes numerical values into quarter-based ranges."""
    if pd.isna(row[col_name]):
        return None
    elif row[col_name] > 1:
        return 'Above 1'
    elif 1 >= row[col_name] > 0.75:
        return '1 to 0.749'
    elif 0.75 >= row[col_name] > 0.5:
        return '0.75 to 0.499'
    elif 0.5 >= row[col_name] > 0.25:
        return '0.5 to 0.249'
    elif 0.25 >= row[col_name] > 0:
        return '0.25 to 0.001'
    elif 0 >= row[col_name] > -0.25:
        return '0 to -0.249'
    elif -0.25 >= row[col_name] > -0.5:
        return '-0.25 to -0.499'
    elif -0.5 >= row[col_name] > -0.75:
        return '-0.5 to -0.749'
    elif -0.75 >= row[col_name] > -1:
        return '-0.75 to -0.999'
    else:
        return 'Beyond -1'

def std_to_halves(row, col_name):
    """Categorizes numerical values into quarter-based ranges."""
    if pd.isna(row[col_name]):
        return None
    elif row[col_name] >= 5:
        return 'Above 5'
    elif 5 > row[col_name] >= 4.5:
        return '4.5 to 4.999'
    elif 4.5 > row[col_name] >= 4:
        return '4 to 4.49'
    elif 4 > row[col_name] >= 3.5:
        return '3.5 to 3.999'
    elif 3.5 > row[col_name] >= 3:
        return '3 to 3.499'
    elif 3 > row[col_name] >= 2.5:
        return '2.5 to 0.299'
    elif 2.5 > row[col_name] >= 2:
        return '2 to 2.499'
    elif 2 > row[col_name] >= 1.5:
        return '1.5 to 1.999'
    elif 1.5 > row[col_name] >= 1:
        return '1 to 1.499'
    elif 1 > row[col_name] >= 0.5:
        return '0.5 to 0.999'
    else:
        return 'Below 0.5'

# ✅ Store username-password pairs
USER_CREDENTIALS = {
    "amer": "NQ",
    "nick": "NQ",
    "tucker": "gamma"
}

# ✅ Initialize session state for authentication
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None

# ✅ Login form (only shown if not authenticated)
if not st.session_state["authenticated"]:
    st.title("Login to M7Box Database")

    # Username and password fields
    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")

    # Submit button
    if st.button("Login"):
        if username in USER_CREDENTIALS and password == USER_CREDENTIALS[username]:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username  # Store the username
            st.success(f"Welcome, {username}! Redirecting...")
            st.rerun()  # Refresh to load the dashboard
        else:
            st.error("Incorrect username or password. Please try again.")

    # Stop execution if user is not authenticated
    st.stop()

# ✅ If authenticated, show the full app
st.sidebar.success(f"Logged in as: **{st.session_state['username']}**")

# ✅ Logout button in the sidebar
if st.sidebar.button("Logout"):
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.rerun()


# Title
st.title("M7Box Database")

# Upload CSV File
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Ensure required column is created
    df['ODR_M7Box_Max_Retracement_STD_Quarters_Grouped'] = df.apply(
        lambda row: std_to_quarter(row, 'ODR_M7Box_Max_Retracement_STD'), axis=1)

    df['RDR_M7Box_Max_Retracement_STD_Quarters_Grouped'] = df.apply(
        lambda row: std_to_quarter(row, 'RDR_M7Box_Max_Retracement_STD'), axis=1)

    df['ODR_DR_Max_Retracement_STD_Quarters_Grouped'] = df.apply(
        lambda row: std_to_quarter(row, 'ODR_DR_Max_Retracement_STD'), axis=1)

    df['RDR_DR_Max_Retracement_STD_Quarters_Grouped'] = df.apply(
        lambda row: std_to_quarter(row, 'RDR_DR_Max_Retracement_STD'), axis=1)

    df['ODR_M7Box_Max_Extension_STD_Halves_Grouped'] = df.apply(
        lambda row: std_to_halves(row, 'ODR_M7Box_Max_Extension_STD'), axis=1)

    df['RDR_M7Box_Max_Extension_STD_Halves_Grouped'] = df.apply(
        lambda row: std_to_halves(row, 'RDR_M7Box_Max_Extension_STD'), axis=1)

    df['ODR_DR_Max_Extension_STD_Halves_Grouped'] = df.apply(
        lambda row: std_to_halves(row, 'ODR_DR_Max_Extension_STD'), axis=1)

    df['RDR_DR_Max_Extension_STD_Halves_Grouped'] = df.apply(
        lambda row: std_to_halves(row, 'RDR_DR_Max_Extension_STD'), axis=1)

    df['ODR_M7Box_Confirmation_Time_NY'] = pd.to_datetime(df['ODR_M7Box_Confirmation_Time_NY'], errors='coerce').dt.time
    df['ODR_DR_Confirmation_Time_NY'] = pd.to_datetime(df['ODR_DR_Confirmation_Time_NY'], errors='coerce').dt.time
    df['RDR_M7Box_Confirmation_Time_NY'] = pd.to_datetime(df['RDR_M7Box_Confirmation_Time_NY'], errors='coerce').dt.time
    df['RDR_DR_Confirmation_Time_NY'] = pd.to_datetime(df['RDR_DR_Confirmation_Time_NY'], errors='coerce').dt.time


    ### **Sidebar: Select Instrument and DR Range**
    instrument_options = df['Instrument'].dropna().unique().tolist()
    selected_instrument = st.sidebar.selectbox("Select Instrument", instrument_options)
    dr_range_options = ['ODR', 'RDR']
    selected_dr_range = st.sidebar.selectbox("Select DR Range", dr_range_options)

    # Plotting columns
    variable_column_1 = f"{selected_dr_range}_M7Box_Max_Retracement_STD_Quarters_Grouped"
    variable_column_2 = f"{selected_dr_range}_DR_Max_Retracement_STD_Quarters_Grouped"
    variable_column_3 = f"{selected_dr_range}_M7Box_Max_Extension_STD_Halves_Grouped"
    variable_column_4 = f"{selected_dr_range}_DR_Max_Extension_STD_Halves_Grouped"

    ### **Main Panel: Filters Above Graph**
    col1, col2 = st.columns(2)

    with col1:
        m7box_direction_options = ['All'] + df[f'{selected_dr_range}_M7Box_Direction'].dropna().unique().tolist()
        selected_m7box_direction = st.selectbox("M7Box Direction", m7box_direction_options)

        m7box_conf_direction_options = ['All'] + df[f'{selected_dr_range}_M7Box_Confirmation_Direction'].dropna().unique().tolist()
        selected_m7box_conf_direction = st.selectbox("M7Box Confirmation Direction", m7box_conf_direction_options)

        dr_confirmation_options = ['All'] + df[f'{selected_dr_range}_DR_Confirmation_Direction'].dropna().unique().tolist()
        selected_dr_confirmation = st.selectbox(f"DR Confirmation Direction", dr_confirmation_options)

    with col2:
        dr_confirmation_valid_options = ['All'] + df[f'{selected_dr_range}_Confirmation_Valid'].dropna().unique().tolist()
        selected_dr_confirmation_valid = st.selectbox("DR Confirmation Valid", dr_confirmation_valid_options)

        m7box_confirmation_valid_options = ['All'] + df[f'{selected_dr_range}_M7Box_Confirmation_Valid'].dropna().unique().tolist()
        selected_m7box_confirmation_valid = st.selectbox("M7Box Confirmation Valid", m7box_confirmation_valid_options)

        dr_model_valid_options = df[f'{selected_dr_range} Model'].dropna().unique().tolist()
        selected_dr_models = st.multiselect(f"Model", ["All"] + dr_model_valid_options, default=["All"])

    # Confirmtion Time
    dr_filtered_time_values = df[f'{selected_dr_range}_DR_Confirmation_Time_NY'].dropna()
    if not dr_filtered_time_values.empty:
        dr_min_time = dr_filtered_time_values.min()
        dr_max_time = dr_filtered_time_values.max()

    m7box_filtered_time_values = df[f'{selected_dr_range}_M7Box_Confirmation_Time_NY'].dropna()
    if not m7box_filtered_time_values.empty:
        m7box_min_time = m7box_filtered_time_values.min()
        m7box_max_time = m7box_filtered_time_values.max()

    # User selects a range (default: full range)
    # Get min and max absolute values (ensuring positive range)
    min_value = df[f'{selected_dr_range} M7Box / IDR'].min()
    max_value = df[f'{selected_dr_range} M7Box / IDR'].max()
    col3, col4, col5 = st.columns([1, 5, 1])

    with col4:
        m7box_selected_time_range = st.slider(
        "Select Time Range for M7Box Confirmation Time (Right Exlusive)",
        min_value=m7box_min_time,
        max_value=m7box_max_time,
        value=(m7box_min_time, m7box_max_time),
        format="HH:mm"
    )

        dr_selected_time_range = st.slider(
        "Select Time Range for DR Confirmation Time (Right Exlusive)",
        min_value=dr_min_time,
        max_value=dr_max_time,
        value=(dr_min_time, dr_max_time),
        format="HH:mm"
    )
        selected_range = st.slider(
            "Select Range for Box Size (Right Exlusive)",
            min_value, max_value, (min_value, max_value)
        )


    ### **Apply Filters (Only if "All" is not selected)**
    filter_columns = [
        ('Instrument', selected_instrument),
        (f'{selected_dr_range}_DR_Confirmation_Direction', selected_dr_confirmation),
        (f'{selected_dr_range}_M7Box_Direction', selected_m7box_direction),
        (f'{selected_dr_range}_Confirmation_Valid', selected_dr_confirmation_valid),
        (f'{selected_dr_range}_M7Box_Confirmation_Valid', selected_m7box_confirmation_valid),
    ]

    for col, val in filter_columns:
        if val != "All":  # **Only apply filter if "None" is NOT selected**
            df = df[df[col] == val]

    # Multi-Select Filtering for RDR Model
    if "All" not in selected_dr_models:
        df = df[df[f'{selected_dr_range} Model'].isin(selected_dr_models)]

    # Conf time and M7Box conf time filter
    df = df[df[f'{selected_dr_range} M7Box / IDR'].between(selected_range[0], selected_range[1], inclusive='left')]

    df = df[(df[f'{selected_dr_range}_M7Box_Confirmation_Time_NY'].notna()) &
            (df[f'{selected_dr_range}_M7Box_Confirmation_Time_NY'] >= m7box_selected_time_range[0]) &
            (df[f'{selected_dr_range}_M7Box_Confirmation_Time_NY'] < m7box_selected_time_range[1])]

    df = df[(df[f'{selected_dr_range}_DR_Confirmation_Time_NY'].notna()) &
            (df[f'{selected_dr_range}_DR_Confirmation_Time_NY'] >= dr_selected_time_range[0]) &
            (df[f'{selected_dr_range}_DR_Confirmation_Time_NY'] < dr_selected_time_range[1])]

    outer_col1, graph_col1, graph_col2, outer_col2 = st.columns([0.1, 11, 11, 0.1])  # Adds margin on left & right

    ret_custom_order = [
        'Beyond -1',
        '-0.75 to -0.999',
        '-0.5 to -0.749',
        '-0.25 to -0.499',
        '0 to -0.249',
        '0.25 to 0.001',
        '0.5 to 0.249',
        '0.75 to 0.499',
        '1 to 0.749',
        'Above 1'
    ]

    ext_custom_order = [
        'Below 0.5',
        '0.5 to 0.999',
        '1 to 1.499',
        '1.5 to 1.999',
        '2 to 2.499',
        '2.5 to 2.999',
        '3 to 3.499',
        '3.5 to 3.999',
        '4 to 4.49',
        '4.5 to 4.999',
        'Above 5'
    ]


    # First Graph with Custom Order
    with graph_col1:

        # M7Box Retracements
        if not df.empty:
            value_counts_df = df[variable_column_1].value_counts().reset_index()
            value_counts_df.columns = [variable_column_1, 'count']
            value_counts_df['percentage'] = (value_counts_df['count'] / value_counts_df['count'].sum()) * 100
            value_counts_df['text'] = value_counts_df.apply(lambda row: f"{row['count']} ({row['percentage']:.2f}%)", axis=1)

            value_counts_df[variable_column_1] = pd.Categorical(
                value_counts_df[variable_column_1], categories=ret_custom_order, ordered=True)
            value_counts_df = value_counts_df.sort_values(by=variable_column_1)

            fig1 = px.bar(
                value_counts_df,
                x=variable_column_1,
                y='count',
                text='text',
                title=f"{selected_dr_range} M7Box Retracements After M7Box Confirmation",
            )
            fig1.update_layout(
                height=500,  # Even taller graph
                margin=dict(l=5, r=5, t=30, b=30),  # Reduce all margins
                xaxis_tickangle=90,  # Keep labels horizontal
            )
            fig1.update_traces(texttemplate='%{text}', textposition='outside', marker_color='#008080')
            fig1.update_layout(yaxis_title="Count",
                               xaxis_title='M7Box Retracements - Distribution',
                               showlegend=False)

            st.plotly_chart(fig1, use_container_width=True)

            # M7Box extensions
            value_counts_df_3 = df[variable_column_3].value_counts().reset_index()
            value_counts_df_3.columns = [variable_column_3, 'count']
            value_counts_df_3['percentage'] = (value_counts_df_3['count'] / value_counts_df_3['count'].sum()) * 100
            value_counts_df_3['text'] = value_counts_df_3.apply(lambda row: f"{row['count']} ({row['percentage']:.2f}%)", axis=1)

            value_counts_df_3[variable_column_3] = pd.Categorical(
                value_counts_df_3[variable_column_3], categories=ext_custom_order, ordered=True)
            value_counts_df_3 = value_counts_df_3.sort_values(by=variable_column_3)

            fig3 = px.bar(
                value_counts_df_3,
                x=variable_column_3,
                y='count',
                text='text',
                title=f"{selected_dr_range} M7Box Extensions After M7Box Confirmation",
            )
            fig3.update_layout(
                height=500,  # Even taller graph
                margin=dict(l=5, r=5, t=30, b=30),  # Reduce all margins
                xaxis_tickangle=90,  # Keep labels horizontal
            )
            fig3.update_traces(texttemplate='%{text}', textposition='outside', marker_color='#008080')
            fig3.update_layout(yaxis_title="Count",
                               xaxis_title='M7Box Extensions - Distribution',
                               showlegend=False)

            st.plotly_chart(fig3, use_container_width=True)

    # DR Retracements
    with graph_col2:
        if not df.empty:
            value_counts_df_2 = df[variable_column_2].value_counts().reset_index()
            value_counts_df_2.columns = [variable_column_2, 'count']
            value_counts_df_2['percentage'] = (value_counts_df_2['count'] / value_counts_df_2['count'].sum()) * 100
            value_counts_df_2['text'] = value_counts_df_2.apply(lambda row: f"{row['count']} ({row['percentage']:.2f}%)", axis=1)

            value_counts_df_2[variable_column_2] = pd.Categorical(
                value_counts_df_2[variable_column_2], categories=ret_custom_order, ordered=True)
            value_counts_df_2 = value_counts_df_2.sort_values(by=variable_column_2)

            fig2 = px.bar(
                value_counts_df_2,
                x=variable_column_2,
                y='count',
                text='text',
                title=f"{selected_dr_range} M7Box Retracements After DR Confirmation",
            )
            fig2.update_layout(
                height=500,  # Even taller graph
                margin=dict(l=5, r=5, t=30, b=30),  # Reduce all margins
                xaxis_tickangle=90,  # Keep labels horizontal
            )
            fig2.update_traces(texttemplate='%{text}', textposition='outside', marker_color='#008080')
            fig2.update_layout(yaxis_title="Count",
                               xaxis_title='M7Box Retracements - Distribution',
                               showlegend=False)

            st.plotly_chart(fig2, use_container_width=True)

            # DR extensions
            value_counts_df_4 = df[variable_column_4].value_counts().reset_index()
            value_counts_df_4.columns = [variable_column_4, 'count']
            value_counts_df_4['percentage'] = (value_counts_df_4['count'] / value_counts_df_4['count'].sum()) * 100
            value_counts_df_4['text'] = value_counts_df_4.apply(lambda row: f"{row['count']} ({row['percentage']:.2f}%)", axis=1)

            value_counts_df_4[variable_column_4] = pd.Categorical(
                value_counts_df_4[variable_column_4], categories=ext_custom_order, ordered=True)
            value_counts_df_4 = value_counts_df_4.sort_values(by=variable_column_4)

            fig4 = px.bar(
                value_counts_df_4,
                x=variable_column_4,
                y='count',
                text='text',
                title=f"{selected_dr_range} M7Box Extensions After DR Confirmation",
            )
            fig4.update_layout(
                height=500,  # Even taller graph
                margin=dict(l=5, r=5, t=30, b=30),  # Reduce all margins
                xaxis_tickangle=90,  # Keep labels horizontal
            )
            fig4.update_traces(texttemplate='%{text}', textposition='outside', marker_color='#008080')
            fig4.update_layout(yaxis_title="Count",
                               xaxis_title='M7Box Extensions - Distribution',
                               showlegend=False)

            st.plotly_chart(fig4, use_container_width=True)
