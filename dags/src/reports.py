"""
Report generation functions for research papers analysis
"""

import json
import logging
from collections import Counter
from pathlib import Path
from typing import Dict, List
import pandas as pd

from .storage import load_processed_data

logger = logging.getLogger(__name__)


def analyze_paper_sources(df: pd.DataFrame) -> Dict:
    """Analyze papers by source"""
    if df.empty:
        return {}
    
    source_counts = df['source'].value_counts()
    return dict(source_counts)


def analyze_top_tools(df: pd.DataFrame, top_n: int = 10) -> List[tuple]:
    """Analyze most mentioned tools and technologies"""
    if df.empty:
        return []
    
    all_tools = []
    for tools_str in df['tools'].dropna():
        if tools_str:
            all_tools.extend([t.strip() for t in tools_str.split(',')])
    
    if not all_tools:
        return []
    
    top_tools = Counter(all_tools).most_common(top_n)
    return top_tools


def get_sample_titles(df: pd.DataFrame, sample_size: int = 5) -> List[str]:
    """Get sample paper titles"""
    if df.empty:
        return []
    
    return df['title'].head(sample_size).tolist()


def generate_summary_report(logical_date: str) -> None:
    """Generate a summary report of the day's paper processing"""
    try:
        df = load_processed_data(logical_date)
        
        logger.info(f"=== Daily Papers Summary for {logical_date} ===")
        logger.info(f"Total MLOps-relevant papers found: {len(df)}")
        
        if len(df) > 0:
            # Analyze sources
            source_analysis = analyze_paper_sources(df)
            logger.info(f"Papers by source: {source_analysis}")
            
            # Analyze top tools
            top_tools = analyze_top_tools(df)
            if top_tools:
                logger.info(f"Top mentioned tools: {top_tools}")
            
            # Sample titles
            sample_titles = get_sample_titles(df)
            logger.info(f"Sample paper titles: {sample_titles}")
        
    except Exception as e:
        logger.error(f"Error generating summary report: {e}")


def generate_detailed_report(logical_date: str) -> Dict:
    """Generate a detailed report with statistics"""
    df = load_processed_data(logical_date)
    
    if df.empty:
        return {
            'date': logical_date,
            'total_papers': 0,
            'sources': {},
            'top_tools': [],
            'sample_titles': [],
            'avg_mlops_score': 0.0
        }
    
    return {
        'date': logical_date,
        'total_papers': len(df),
        'sources': analyze_paper_sources(df),
        'top_tools': analyze_top_tools(df),
        'sample_titles': get_sample_titles(df),
        'avg_mlops_score': df['mlops_score'].mean() if 'mlops_score' in df.columns else 0.0
    }


def _convert_numpy_types(obj):
    """Convert numpy types to native Python types for JSON serialization"""
    import numpy as np
    
    if isinstance(obj, dict):
        return {key: _convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_convert_numpy_types(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(_convert_numpy_types(item) for item in obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj


def save_summary_report(logical_date: str) -> str:
    """Save a detailed summary report to JSON file"""
    try:
        # Generate the detailed report
        report_data = generate_detailed_report(logical_date)
        
        # Convert numpy types to native Python types
        report_data = _convert_numpy_types(report_data)
        
        # Create reports directory
        date_str = logical_date.replace('-', '')  # Convert YYYY-MM-DD to YYYYMMDD
        reports_dir = Path("data/reports")
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Save as JSON file
        report_file = reports_dir / f"{date_str}_summary.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved summary report to {report_file}")
        return str(report_file)
        
    except Exception as e:
        logger.error(f"Error saving summary report: {e}")
        return ""


def save_detailed_markdown_report(logical_date: str) -> str:
    """Save a detailed markdown report"""
    try:
        # Generate the detailed report data
        report_data = generate_detailed_report(logical_date)
        
        # Create reports directory
        date_str = logical_date.replace('-', '')  # Convert YYYY-MM-DD to YYYYMMDD
        reports_dir = Path("data/reports")
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate markdown content
        markdown_content = f"""# Daily Papers Summary Report
        
**Date:** {logical_date}

## Overview
- **Total MLOps-relevant papers found:** {report_data['total_papers']}
- **Average MLOps relevance score:** {report_data['avg_mlops_score']:.2f}

## Papers by Source
"""
        
        if report_data['sources']:
            for source, count in report_data['sources'].items():
                markdown_content += f"- **{source}:** {count} papers\n"
        else:
            markdown_content += "- No papers found\n"
        
        markdown_content += "\n## Top Mentioned Tools\n"
        
        if report_data['top_tools']:
            for i, (tool, count) in enumerate(report_data['top_tools'][:10], 1):
                markdown_content += f"{i}. **{tool}** ({count} mentions)\n"
        else:
            markdown_content += "- No tools identified\n"
        
        markdown_content += "\n## Sample Paper Titles\n"
        
        if report_data['sample_titles']:
            for i, title in enumerate(report_data['sample_titles'], 1):
                markdown_content += f"{i}. {title}\n"
        else:
            markdown_content += "- No papers to display\n"
        
        # Save markdown file
        report_file = reports_dir / f"{date_str}_summary.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        logger.info(f"Saved markdown report to {report_file}")
        return str(report_file)
        
    except Exception as e:
        logger.error(f"Error saving markdown report: {e}")
        return "" 
