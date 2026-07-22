# EduTracker Analytics Workspace

This workspace is for the analytics and data processing tasks of the EduTracker project.

## Setup

Follow these steps to set up the development environment:

1. Clone the repository:
   ```bash
   git clone https://github.com/kalviumcommunity/EduTracker.git
   cd EduTracker
   ```

2. Create a virtual environment:
   - macOS/Linux: `python3 -m venv venv`
   - Windows: `python -m venv venv`

3. Activate the virtual environment:
   - macOS/Linux: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate`

4. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Project Structure

- `data/raw/`: This directory contains raw, unmodified data files.
- `data/processed/`: This directory contains cleaned and processed data files.
- `notebooks/`: This directory contains Jupyter notebooks for exploration and analysis.
- `scripts/`: This directory contains Python scripts for automation and processing.
- `output/`: This directory contains generated outputs such as figures and reports.

## Notes

- Copy `.env.example` to `.env` and fill in your own environment variable values.
- Do not commit the `.env` file to version control.