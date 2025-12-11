# Web Scraper and Data Analysis Dashboard

This project is a web scraping application that gathers data from multiple e-commerce sites and provides a web-based dashboard for data analysis and visualization.

## Features

- **Cyclic Scraping**: Automatically scrapes predefined URLs at regular intervals.
- **Interactive Dashboard**: A web-based interface to view, filter, and analyze scraped data.
- **Data Visualization**: Interactive charts and tables to visualize price trends.
- **Manual Scrape**: Ability to trigger a scrape manually from the dashboard.
- **Data Export**: Export scraped data to CSV.
- **Email Alerts**: Optional email notifications.
- **robots.txt**: Respects `robots.txt` by default.

## Project Structure

- `main.py`: The main entry point for running the cyclical scraper.
- `Panel.py`: The Streamlit-based web dashboard.
- `scraper/`: Directory containing the core scraping logic.
- `requirements.txt`: A list of all the dependencies for this project.
- `config.json`: Configuration file for email alerts and `robots.txt` settings.
- `scraped_data.db`: The SQLite database where the scraped data is stored.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create and activate a virtual environment:**
    - On Windows:
      ```bash
      python -m venv .venv
      .venv\Scripts\activate
      ```
    - On macOS/Linux:
      ```bash
      python3 -m venv .venv
      source .venv/bin/activate
      ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## How to Run

This project can be run in two ways: as a command-line application for continuous scraping or as a web-based dashboard for interactive analysis.

### 1. Command-Line Interface (for continuous scraping)

To start the scraper in continuous mode, run `main.py`. The scraper will run at a specified interval, and you will be prompted to enter the interval in minutes.

```bash
python main.py
```

### 2. Web Dashboard (for interactive analysis)

To launch the web dashboard, use Streamlit to run `Panel.py`. This will open a new tab in your web browser with the dashboard.

```bash
streamlit run Panel.py
```

From the dashboard, you can:
- View and analyze the scraped data.
- Manually trigger a one-time scrape.
- Configure email alerts and `robots.txt` settings.
- Export data to a CSV file.

## Configuration

The application can be configured using the `config.json` file. If the file does not exist, it will be created with default settings when you save settings in the web dashboard. These settings can also be configured from the web dashboard.

- `respect_robots_txt`: Whether to follow the rules specified in the websites' `robots.txt` files (default: `true`).
- `email_address`: The email address to which notifications will be sent.
- `alerts_enabled`: Whether to enable email notifications (default: `false`).
- `sender_email`: The email address from which notifications will be sent.
- `sender_password`: The password for the sender's email account.

**Note:** The application uses Ethereal Email for testing purposes. These are temporary accounts. You will need to manually update `sender_email` and `sender_password` in the `config.json` file with your own email credentials to receive email alerts.