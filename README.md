# HAR files to csv

This is a simple script to convert HAR files to CSV files to quickly import network requests in Google Sheets.

## Requirements

- Python 3.11 or higher (may work with older versions but not tested)
- Google Chrome

## Installation

1. Clone the repository or download the files.
2. Create a virtual environment with `python -m venv venv` and activate it with `source venv/bin/activate` on WSL2.
3. Install the requirements with `pip install -r requirements.txt`.

## Usage

1. Open a Chrome private window on the desired start page and open the developer tools (F12) on the network tab. Clear previous logs and enable "Preserve log".
2. Hard reload the page (Ctrl + F5) and wait for the page to load and all requests to finish.
3. Accept or deny consents if necessary and browse a few pages.
4. When done, click on the "Export HAR" button at the top of the network tab and save the file in the input_files_har folder.
5. Repeat steps 1 to 4 for each domain to analyze.
6. Copy the `config.yml.example` file and renamme it to `config.yml`, then adapt the configurations to your needs.
7. Run the script with the command `python main.py` from the terminal.
8. A unique CSV file will be saved in the output_files_csv folder.
9. Import the CSV files Google Sheets and analyze the data.
