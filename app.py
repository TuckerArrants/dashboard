import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(layout='wide')

def dynamic_binning(df, col_name, bin_width=0.25):
    if col_name not in df or df[col_name].dropna().empty:
        return None, []  # Return None and an empty list if the column doesn't exist or is empty

    col_min = df[col_name].min(skipna=True)
    col_max = df[col_name].max(skipna=True)

    # Round min/max to nearest bin width
    col_min = bin_width * np.floor(col_min / bin_width)
    col_max = bin_width * np.ceil(col_max / bin_width)

    # Create bins explicitly in increments of bin_width
    bins = np.arange(col_min, col_max + bin_width, bin_width)

    # Generate labels dynamically with correct formatting
    labels = []
    for i in range(len(bins) - 1):
        lower, upper = bins[i], bins[i + 1] - 0.001  # Adjust upper bound for correct naming
        labels.append(f"{lower:.3f} to {upper:.3f}")

    # Apply binning to the column
    categorized_column = pd.cut(df[col_name], bins=bins, labels=labels, include_lowest=True)

    return categorized_column, labels  # Return labels in descending order (from high to low)

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
st.title("M7Box Database")

# ✅ Logout button in the sidebar
if st.sidebar.button("Logout"):
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.rerun()

# Upload CSV File
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Ensure required column is created
    df['ODR_M7Box_Max_Retracement_STD_Quarters_Grouped'], odr_m7box_ret_custom_order = dynamic_binning(df, 'ODR_M7Box_Max_Retracement_STD', bin_width=0.25)
    df['RDR_M7Box_Max_Retracement_STD_Quarters_Grouped'], rdr_m7Box_ret_custom_order= dynamic_binning(df, 'RDR_M7Box_Max_Retracement_STD', bin_width=0.25)
    df['ODR_DR_Max_Retracement_STD_Quarters_Grouped'], odr_dr_ret_custom_order = dynamic_binning(df, 'ODR_DR_Max_Retracement_STD', bin_width=0.25)
    df['RDR_DR_Max_Retracement_STD_Quarters_Grouped'], rdr_dr_ret_custom_order= dynamic_binning(df, 'RDR_DR_Max_Retracement_STD', bin_width=0.25)

    df['ODR_M7Box_Max_Extension_STD_Halves_Grouped'], odr_m7box_ext_custom_order = dynamic_binning(df, 'ODR_M7Box_Max_Extension_STD', bin_width=0.5)
    df['RDR_M7Box_Max_Extension_STD_Halves_Grouped'], rdr_m7Box_ext_custom_order= dynamic_binning(df, 'RDR_M7Box_Max_Extension_STD', bin_width=0.5)
    df['ODR_DR_Max_Extension_STD_Halves_Grouped'], odr_dr_ext_custom_order = dynamic_binning(df, 'ODR_DR_Max_Extension_STD', bin_width=0.5)
    df['RDR_DR_Max_Extension_STD_Halves_Grouped'], rdr_dr_ext_custom_order = dynamic_binning(df, 'RDR_DR_Max_Extension_STD', bin_width=0.5)

    df['ODR_M7Box_Confirmation_Time_NY'] = pd.to_datetime(df['ODR_M7Box_Confirmation_Time_NY'], errors='coerce').dt.time
    df['ODR_DR_Confirmation_Time_NY'] = pd.to_datetime(df['ODR_DR_Confirmation_Time_NY'], errors='coerce').dt.time
    df['RDR_M7Box_Confirmation_Time_NY'] = pd.to_datetime(df['RDR_M7Box_Confirmation_Time_NY'], errors='coerce').dt.time
    df['RDR_DR_Confirmation_Time_NY'] = pd.to_datetime(df['RDR_DR_Confirmation_Time_NY'], errors='coerce').dt.time

    ### **Sidebar: Select Instrument and DR Range**
    instrument_options = df['Instrument'].dropna().unique().tolist()
    selected_instrument = st.sidebar.selectbox("Select Instrument", instrument_options)
    dr_range_options = ['ODR', 'RDR']
    selected_dr_range = st.sidebar.selectbox("Select DR Range", dr_range_options)
    day_options = ['All'] + ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    selected_day = st.sidebar.selectbox("Day if Week", day_options)

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
        (f'{selected_dr_range}_M7Box_Confirmation_Direction', selected_m7box_conf_direction),
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

######################################################
### Metric Tiles
######################################################
    total_count = len(df)

    # Probability of hitting -1 (or less)
    prob_neg_1 = df[df[f'{selected_dr_range}_M7Box_Max_Retracement_STD'] <= -1].shape[0] / total_count if total_count > 0 else 0
    # Probability of hitting 0
    prob_0 = df[df[f'{selected_dr_range}_M7Box_Max_Retracement_STD'] <= 0].shape[0] / total_count if total_count > 0 else 0

    # Probability of hitting -1 (or less)
    prob_neg_1_dr = df[df[f'{selected_dr_range}_DR_Max_Retracement_STD'] <= -1].shape[0] / total_count if total_count > 0 else 0

    # Probability of hitting 0
    prob_0_dr = df[df[f'{selected_dr_range}_DR_Max_Retracement_STD'] <= 0].shape[0] / total_count if total_count > 0 else 0

    # ✅ Step 2: Create 4 Stat Panels
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="% of Hitting -1 After M7Box Conf.", value=f"{prob_neg_1:.2%}")

    with col2:
        st.metric(label="% of Hitting 0 After M7Box Conf.", value=f"{prob_0:.2%}")

    with col3:
        st.metric(label="% of Hitting -1 After DR Conf.", value=f"{prob_neg_1_dr:.2%}")

    with col4:
        st.metric(label="% of Hitting 0 After DR Conf.", value=f"{prob_0_dr:.2%}")

######################################################
### Retracement Graphs
######################################################

    outer_col1, graph_col1, graph_col2, outer_col2 = st.columns([0.1, 11, 11, 0.1])  # Adds margin on left & right

    m7box_ret_custom_order = odr_m7box_ret_custom_order if selected_dr_range == 'ODR' else rdr_m7Box_ret_custom_order
    m7box_ext_custom_order = odr_m7box_ext_custom_order if selected_dr_range == 'ODR' else rdr_m7Box_ext_custom_order

    dr_ret_custom_order = odr_dr_ret_custom_order if selected_dr_range == 'ODR' else rdr_dr_ret_custom_order
    dr_ext_custom_order = odr_dr_ext_custom_order if selected_dr_range == 'ODR' else rdr_dr_ext_custom_order


    # First Graph with Custom Order
    with graph_col1:

        # M7Box Retracements
        if not df.empty:
            value_counts_df = df[variable_column_1].value_counts().reset_index()
            value_counts_df.columns = [variable_column_1, 'count']
            value_counts_df['percentage'] = (value_counts_df['count'] / value_counts_df['count'].sum()) * 100
            value_counts_df['text'] = value_counts_df.apply(lambda row: f"{row['count']} ({row['percentage']:.2f}%)", axis=1)

            value_counts_df[variable_column_1] = pd.Categorical(
                value_counts_df[variable_column_1], categories=m7box_ret_custom_order, ordered=True)
            value_counts_df = value_counts_df.sort_values(by=variable_column_1)

            fig1 = px.bar(
                value_counts_df,
                x=variable_column_1,
                y='count',
                text='text',
                title=f"{selected_dr_range} M7Box Retracements After M7Box Confirmation",
            )

            # Get the 30th and 70th percentile values for default zoom
            default_y_min = value_counts_df['count'].quantile(0.3)
            default_y_max = value_counts_df['count'].quantile(0.7)

            # Ensure default_y_min and default_y_max are valid numbers
            if pd.isna(default_y_min) or pd.isna(default_y_max):
                default_y_min = value_counts_df['count'].min()
                default_y_max = value_counts_df['count'].max()

            # Add a small buffer to default_y_max for better visualization
            default_y_max *= 1.1  # Add 10% padding

            fig1.update_layout(
                height=500,  # Even taller graph
                margin=dict(l=5, r=5, t=30, b=30),  # Reduce all margins
                xaxis_tickangle=90, # Keep labels horizontal

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
                value_counts_df_3[variable_column_3], categories=m7box_ext_custom_order, ordered=True)
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
                value_counts_df_2[variable_column_2], categories=dr_ret_custom_order, ordered=True)
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
                value_counts_df_4[variable_column_4], categories=dr_ext_custom_order, ordered=True)
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
