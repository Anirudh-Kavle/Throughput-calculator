import streamlit as st
import pandas as pd
import io
import base64
import numpy as np
import os

# Set page config
st.set_page_config(
    page_title="CQI Throughput Calculator",
    page_icon="📊",
    layout="wide"
)

# Define CSS for a more polished UI
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .title {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    .subtitle {
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stDownloadButton button {
        background-color: #4CAF50;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Title and introduction
st.markdown("<h1 class='title'>CQI Throughput Calculator</h1>", unsafe_allow_html=True)
st.markdown("""
This application processes your CQI actual vs prediction data to:
- Calculate throughput values based on CQI indices
- Determine throughput efficiency (Predicted/Actual)
- Allow downloading of processed data
""")

# Read CQI table from local file
@st.cache
def get_cqi_table():
    try:
        cqi_table_file = "CQI_table.csv"
        if os.path.exists(cqi_table_file):
            cqi_table_df = pd.read_csv(cqi_table_file)
            # Clean the data
            cqi_table_df = cqi_table_df.replace('-', '0')  # Replace '-' with '0' for conversion
            cqi_table_df[['CQI index', 'code rate x 1024', 'efficiency']] = cqi_table_df[['CQI index', 'code rate x 1024', 'efficiency']].astype(float)
            return cqi_table_df
        else:
            st.error(f"CQI table file not found: {cqi_table_file}")
            return None
    except Exception as e:
        st.error(f"Error loading CQI table: {str(e)}")
        return None

# Function to create a download link for the dataframe
def get_download_link(df, filename, text):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

# Function to calculate throughput based on CQI value
def calculate_throughput(cqi_value, cqi_lookup, bandwidth=100):
    if cqi_value in cqi_lookup.index:
        code_rate_1024 = cqi_lookup.loc[cqi_value, 'code rate x 1024']
        efficiency = cqi_lookup.loc[cqi_value, 'efficiency']
        return (code_rate_1024 / 1024) * efficiency * bandwidth
    return 0  # Default to 0 if CQI is not found

# Function to process a single file
def process_file(uploaded_file, actual_col, pred_col, bandwidth):
    try:
        # Read the uploaded file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(uploaded_file)
        else:
            st.error(f"Unsupported file format: {uploaded_file.name}")
            return None
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Check if columns exist
        if actual_col not in df.columns:
            st.error(f"Column '{actual_col}' not found in the file. Available columns: {', '.join(df.columns)}")
            return None
        
        if pred_col not in df.columns:
            st.error(f"Column '{pred_col}' not found in the file. Available columns: {', '.join(df.columns)}")
            return None
        
        # Get CQI lookup table
        cqi_table_df = get_cqi_table()
        if cqi_table_df is None:
            return None
            
        cqi_lookup = cqi_table_df.set_index('CQI index')[['code rate x 1024', 'efficiency']]
        
        # Calculate actual throughput
        df['Actual Throughput'] = df[actual_col].apply(lambda x: calculate_throughput(x, cqi_lookup, bandwidth))
        
        # Initialize predicted throughput column
        df['Predicted Throughput'] = 0.0
        
        # Only calculate throughput when Pred CQI <= Actual CQI (indicating valid prediction)
        mask = df[pred_col] <= df[actual_col]
        df.loc[mask, 'Predicted Throughput'] = df.loc[mask, pred_col].apply(
            lambda x: calculate_throughput(x, cqi_lookup, bandwidth)
        )
        
        # Calculate throughput efficiency (as a percentage)
        df['Throughput Efficiency'] = np.where(
            df['Actual Throughput'] > 0,
            (df['Predicted Throughput'] / df['Actual Throughput']) * 100,
            0
        )
        
        # Round the results for better readability
        df['Actual Throughput'] = df['Actual Throughput'].round(4)
        df['Predicted Throughput'] = df['Predicted Throughput'].round(4)
        df['Throughput Efficiency'] = df['Throughput Efficiency'].round(2)
        
        return df
    
    except Exception as e:
        st.error(f"Error processing file {uploaded_file.name}: {str(e)}")
        return None

# Main app interface
with st.container():
    st.markdown("<h2 class='subtitle'>Upload Files</h2>", unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader("Upload CQI actual vs prediction files (CSV or Excel)", 
                                     type=['csv', 'xlsx', 'xls'], 
                                     accept_multiple_files=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        actual_col = st.text_input("Name of Actual CQI column", "Actual")
    
    with col2:
        pred_col = st.text_input("Name of Predicted CQI column", "Pred")
    
    with col3:
        bandwidth = st.number_input("Bandwidth (MHz)", min_value=1, value=100, step=1)

    process_button = st.button("Process Files")

# Process files when button is clicked
if process_button and uploaded_files:
    # Check if CQI table is available
    cqi_table = get_cqi_table()
    if cqi_table is None:
        st.error("Cannot proceed without valid CQI table. Please ensure 'CQI_table.csv' is in the working directory.")
    else:
        with st.spinner("Processing files..."):
            all_results = {}
            
            for uploaded_file in uploaded_files:
                st.markdown(f"### Processing: {uploaded_file.name}")
                
                result_df = process_file(uploaded_file, actual_col, pred_col, bandwidth)
                
                if result_df is not None:
                    all_results[uploaded_file.name] = result_df
                    
                    # Display file results
                    with st.container():
                        # Show summary metrics in a nice format
                        avg_efficiency = result_df['Throughput Efficiency'].mean()
                        
                        st.markdown(
                            f"""<div class='metric-card'>
                                <h3>Average Throughput Efficiency</h3>
                                <h2>{avg_efficiency:.2f}%</h2>
                            </div>""", 
                            unsafe_allow_html=True
                        )
                        
                        # Data preview
                        st.subheader("Data Preview")
                        st.dataframe(result_df.head(10))
                        
                        # Download link
                        output_filename = f"processed_{uploaded_file.name.split('.')[0]}.csv"
                        st.markdown(
                            get_download_link(result_df, output_filename, f"Download Processed Data: {output_filename}"),
                            unsafe_allow_html=True
                        )
                        
                        st.markdown("---")
            
            if len(all_results) > 1:
                st.markdown("### Combined Results Summary")
                
                # Calculate combined statistics
                all_efficiencies = pd.concat([df['Throughput Efficiency'] for df in all_results.values()])
                combined_avg_efficiency = all_efficiencies.mean()
                
                st.markdown(
                    f"""<div class='metric-card'>
                        <h3>Combined Average Throughput Efficiency</h3>
                        <h2>{combined_avg_efficiency:.2f}%</h2>
                    </div>""", 
                    unsafe_allow_html=True
                )
                
                st.info("Each file has its individual download link above.")

else:
    if not uploaded_files and process_button:
        st.warning("Please upload at least one file to process.")
    elif not process_button:
        st.info("Upload your files and click 'Process Files' to begin analysis.")