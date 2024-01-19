from fastapi import FastAPI, UploadFile, Form, File, HTTPException
import pandas as pd
import numpy as np

app = FastAPI()


# Function to calculate daily returns
def calculate_daily_returns(data):
    data['Daily Returns'] = data['Close '].pct_change()
    return data


# Function to calculate daily volatility
def calculate_daily_volatility(data):
    data['Daily Volatility'] = data['Daily Returns'].std()
    return data['Daily Volatility'].iloc[-1]


# Function to calculate annualized volatility
def calculate_annualized_volatility(daily_volatility, data_length):
    annualized_volatility = daily_volatility * np.sqrt(data_length)
    return annualized_volatility


@app.post("/compute_volatility")
async def compute_volatility(
        file: UploadFile = File(None),
        directory: str = Form(None)
):
    """
    Compute Daily and Annualized Volatility.

    Parameters:
    - file: Upload a CSV file.
    - directory: Fetch data from a directory.

    Returns:
    - Daily Volatility
    - Annualized Volatility
    """
    if not file and not directory:
        raise HTTPException(status_code=400, detail="Either provide a CSV file or a directory parameter.")

    try:
        if file:
            # Read data from the uploaded CSV file
            data_frame = pd.read_csv(file.file)
        elif directory:
            # Read data from the specified directory
            # Replace 'your_dataset.csv' with the actual file name in the directory
            data_frame = pd.read_csv(directory)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="CSV file not found in the specified directory.")

    # Step 1: Calculate daily returns
    daily_returns = calculate_daily_returns(data_frame)

    # Step 2: Calculate daily volatility
    daily_volatility = calculate_daily_volatility(daily_returns)

    # Step 3: Calculate annualized volatility
    data_length = len(data_frame)
    annualized_volatility = calculate_annualized_volatility(daily_volatility, data_length)

    return {
        "Daily Volatility": round(daily_volatility, 4),
        "Annualized Volatility": round(annualized_volatility, 4)
    }
