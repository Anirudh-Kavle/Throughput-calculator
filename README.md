# CQI Throughput Calculator

A web application for analyzing and comparing Channel Quality Indicator (CQI) actual vs. predicted data, calculating throughput, and evaluating throughput efficiency. Built with [Streamlit](https://streamlit.io/), it provides an interactive interface for uploading data files, processing them, and downloading results.

---

## Features

- **Upload multiple files** (CSV or Excel) containing CQI actual and predicted values.
- **Automatic throughput calculation** based on CQI indices and a reference table.
- **Throughput efficiency analysis** (Predicted/Actual).
- **Download processed results** for each file.
- **Combined summary statistics** when multiple files are processed.
- **User-friendly interface** with summary metrics and data previews.

---

## Installation

1. **Clone the repository** (or download the files):

   ```sh
   git clone https://github.com/Anirudh-Kavle/Throughput-calculator
   cd Throughput-calculator-app
   ```

2. **Install dependencies** (preferably in a virtual environment):

   ```sh
   pip install -r req.txt
   ```

---

## Usage

1. **Ensure `CQI_table.csv` is present** in the project directory. This file is required for throughput calculations.

2. **Prepare your data files**:
   - Supported formats: `.csv`, `.xls`, `.xlsx`
   - Each file should have columns for actual and predicted CQI values (default names: `Actual` and `Pred`).

3. **Run the application**:

   ```sh
   streamlit run app.py
   ```

4. **Open the web interface** (Streamlit will provide a local URL, e.g., `http://localhost:8501`).

5. **Using the app**:
   - Upload one or more CQI data files.
   - Specify the column names for actual and predicted CQI (if different from defaults).
   - Set the bandwidth (in MHz) for throughput calculation.
   - Click **Process Files**.
   - View summary metrics, data previews, and download processed results.

---

## How It Works

### 1. CQI Table Loading

The app loads `CQI_table.csv` ([CQI_table.csv](CQI_table.csv)), which maps each CQI index to its modulation, code rate, and efficiency. This table is used as a lookup for throughput calculations.

### 2. File Processing

For each uploaded file:
- Reads the file using pandas.
- Cleans column names and checks for the specified actual and predicted CQI columns.
- Calculates **Actual Throughput** and **Predicted Throughput** for each row using the formula:

  ```
  Throughput = (code rate x 1024 / 1024) * efficiency * bandwidth
  ```

- **Predicted Throughput** is only calculated when the predicted CQI is less than or equal to the actual CQI.
- **Throughput Efficiency** is computed as:

  ```
  Throughput Efficiency (%) = (Predicted Throughput / Actual Throughput) * 100
  ```

- Results are rounded for readability.

### 3. Results Display

- For each file, the app displays:
  - Average throughput efficiency.
  - Data preview (first 10 rows).
  - Download link for the processed file.
- If multiple files are processed, a combined summary of throughput efficiency is shown.

### 4. Code Overview

- Main logic is in [app.py](app.py).
- Uses Streamlit for UI, pandas for data handling, numpy for calculations, and base64 for download links.
- The CQI table is loaded and cached for performance.
- All processing is handled in the `process_file` function.

---

## Example

Suppose you have a file `sample.csv`:

| Actual | Pred |
|--------|------|
| 7      | 6    |
| 10     | 9    |
| 12     | 12   |

Upload this file, set the column names if needed, and process. The app will compute throughput and efficiency for each row and allow you to download the results.

---

## Dependencies

See [req.txt](req.txt):

- streamlit
- pandas
- numpy
- io
- base64
- matplotlib
- seaborn

---
