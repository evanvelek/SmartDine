# SmartDine API Server Setup & Run Guide

This guide explains how to download, install, and run the SmartDine API server.

------------------------------------------------------------------------

## 0) Prerequisites

-   **Python 3.12 (64-bit)** installed

    Verify:

        py -3.12 --version


------------------------------------------------------------------------

## 1) Download the server folder 

-   Open Command Prompt in the top folder with `main.py`

------------------------------------------------------------------------

## 2) Create and Activate Virtual Environment

From the server folder:

    rmdir /s /q .venv
    py -3.12 -m venv .venv
    .venv\Scripts\activate
    python --version

Make sure it prints **Python 3.12.x**.

------------------------------------------------------------------------

## 3) Install Dependencies

    python -m pip install --upgrade pip
    pip install -r requirements.txt

If installation fails due to Rust/pydantic issues, ensure you are using
Python 3.12 and that `requirements.txt` does not pin an incompatible
pydantic version.

------------------------------------------------------------------------

## 4) Yelp API Key is in .env

Just FYI, no action needed. The Yep API Key is in `.env`, in the same directory as main.py


------------------------------------------------------------------------

## 5) Initialize / Seed Database

Run seed_dd.py to initialize the database:
    python seed_db.py

------------------------------------------------------------------------

## 6) Run the api Server

    uvicorn main:app --reload --port 8000

If uvicorn command fails, run it this way instead:

    python -m uvicorn main:app --reload --port 8000

You should see:

    Uvicorn running on http://127.0.0.1:8000

------------------------------------------------------------------------

## 7) Test the server

### Option A: Swagger UI

Open browser:

    http://127.0.0.1:8000/docs

Test `POST /recommend`.

### Option B: Use the Mock UI Script provided

Open a second terminal in the same folder:

    .venv\Scripts\activate
    python mock_ui.py

You should see JSON with: - `generated_at` - `recommendations` (top 3)

------------------------------------------------------------------------

## 8) Flutter Connection Ideas ....

### Android Emulator

Use:

    http://10.0.2.2:8000

### Real Phone (same WiFi)

Use your PC's local IP:

    http://<YOUR_PC_IP>:8000

Find your PC IP:

    ipconfig

Do NOT use `localhost` from emulator or phone.

CORS is enabled, so cross-origin requests are allowed.

------------------------------------------------------------------------

## Common Issues

### pip install fails (Rust/pydantic errors)

-   Ensure Python 3.12 is installed
-   Ensure correct virtual environment is activated

### Flutter cannot reach 

-   Use `10.0.2.2` for emulator
-   Use LAN IP for real device

### Yelp returns 401

-   `.env` missing or incorrect
-   Server not restarted after adding API key

------------------------------------------------------------------------
