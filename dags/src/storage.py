"""
Data storage and file operations for research papers
"""

import logging
from pathlib import Path
from typing import Dict, List
import pandas as pd

logger = logging.getLogger(__name__)


def get_file_path(date_str: str, data_type: str) -> Path:
    """Generate file path for data storage"""
    return Path(f"data/{data_type}/{date_str}.csv")


def save_papers_to_csv(papers: List[Dict], file_path: Path) -> None:
    """Save papers list to CSV file"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    if not papers:
        # Create empty file to maintain consistency
        pd.DataFrame().to_csv(file_path, index=False)
        return
    
    df = pd.DataFrame(papers)
    df.to_csv(file_path, index=False)


def save_raw_data(papers: List[Dict], logical_date: str) -> str:
    """Save raw paper data to CSV file"""
    date_str = logical_date.replace('-', '')  # Convert YYYY-MM-DD to YYYYMMDD
    raw_file = get_file_path(date_str, 'raw')
    
    if not papers:
        logger.warning("No papers to save")
        save_papers_to_csv(papers, raw_file)
        return str(raw_file)
    
    save_papers_to_csv(papers, raw_file)
    logger.info(f"Saved {len(papers)} raw papers to {raw_file}")
    return str(raw_file)


def save_processed_data(processed_papers: List[Dict], logical_date: str) -> str:
    """Save processed and classified paper data to CSV file"""
    date_str = logical_date.replace('-', '')  # Convert YYYY-MM-DD to YYYYMMDD
    processed_file = get_file_path(date_str, 'processed')
    
    if not processed_papers:
        logger.warning("No processed papers to save")
        save_papers_to_csv(processed_papers, processed_file)
        return str(processed_file)
    
    save_papers_to_csv(processed_papers, processed_file)
    logger.info(f"Saved {len(processed_papers)} processed papers to {processed_file}")
    return str(processed_file)


def load_processed_data(logical_date: str) -> pd.DataFrame:
    """Load processed data for a specific date"""
    date_str = logical_date.replace('-', '')
    processed_file = get_file_path(date_str, 'processed')
    
    if processed_file.exists():
        return pd.read_csv(processed_file)
    else:
        logger.warning(f"No processed data file found for {logical_date}")
        return pd.DataFrame() 
