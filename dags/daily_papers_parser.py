from __future__ import annotations

import logging
from typing import Dict, List

import pendulum
from airflow.sdk import dag, task

# Import our custom modules
from src.parsers import parse_huggingface_papers, parse_all_arxiv_papers, combine_papers
from src.classifiers import classify_papers_mlops_relevance
from src.storage import save_raw_data, save_processed_data
from src.reports import generate_summary_report, save_summary_report, save_detailed_markdown_report

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dag(
    schedule="0 9 * * *",  # Daily at 9 AM
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    catchup=False,
    tags=["papers", "research", "mlops", "daily"],
)
def daily_papers_parser():
    """
    ### Daily Research Papers Parser and Classifier
    
    This DAG scrapes research papers from multiple sources daily and classifies
    them for MLOps/LLMOps relevance. It features enhanced abstract fetching
    that retrieves full abstracts directly from individual paper pages.
    
    The DAG is refactored with modular components:
    - src.parsers: Web scraping with enhanced abstract fetching
    - src.classifiers: MLOps relevance classification
    - src.storage: Data saving and file operations  
    - src.reports: Summary report generation and saving
    
    Outputs:
    - data/raw/{YYYYMMDD}.csv: Raw scraped papers
    - data/processed/{YYYYMMDD}.csv: MLOps-classified papers
    - data/reports/{YYYYMMDD}_summary.json: Detailed JSON report
    - data/reports/{YYYYMMDD}_summary.md: Human-readable Markdown report
    """

    @task
    def parse_huggingface_papers_task(**context) -> List[Dict]:
        """Parse papers from Hugging Face daily papers page"""
        return parse_huggingface_papers()

    @task
    def parse_arxiv_papers_task(**context) -> List[Dict]:
        """Parse papers from all ArXiv categories"""
        return parse_all_arxiv_papers()

    @task
    def combine_papers_task(hf_papers: List[Dict], arxiv_papers: List[Dict], **context) -> List[Dict]:
        """Combine papers from all sources"""
        return combine_papers(hf_papers, arxiv_papers)

    @task
    def save_raw_data_task(papers: List[Dict], **context) -> str:
        """Save raw paper data to CSV file"""
        logical_date = context['ds']  # YYYY-MM-DD format
        return save_raw_data(papers, logical_date)

    @task
    def classify_mlops_relevance_task(papers: List[Dict], **context) -> List[Dict]:
        """Classify papers for MLOps/LLMOps relevance and extract metadata"""
        return classify_papers_mlops_relevance(papers)

    @task
    def save_processed_data_task(processed_papers: List[Dict], **context) -> str:
        """Save processed and classified paper data to CSV file"""
        logical_date = context['ds']  # YYYY-MM-DD format
        return save_processed_data(processed_papers, logical_date)

    @task
    def generate_summary_report_task(**context) -> None:
        """Generate a summary report of the day's paper processing"""
        logical_date = context['ds']
        generate_summary_report(logical_date)

    @task
    def save_summary_report_task(**context) -> str:
        """Save detailed summary report to JSON file"""
        logical_date = context['ds']
        return save_summary_report(logical_date)

    @task
    def save_markdown_report_task(**context) -> str:
        """Save detailed summary report to Markdown file"""
        logical_date = context['ds']
        return save_detailed_markdown_report(logical_date)

    # Define the workflow
    hf_papers = parse_huggingface_papers_task()
    arxiv_papers = parse_arxiv_papers_task()
    all_papers = combine_papers_task(hf_papers, arxiv_papers)
    
    raw_file = save_raw_data_task(all_papers)
    processed_papers = classify_mlops_relevance_task(all_papers)
    processed_file = save_processed_data_task(processed_papers)
    summary_report = generate_summary_report_task()
    json_report = save_summary_report_task()
    markdown_report = save_markdown_report_task()
    
    # Set dependencies
    [raw_file, processed_papers] >> processed_file >> [summary_report, json_report, markdown_report]


# Instantiate the DAG
daily_papers_parser() 
 