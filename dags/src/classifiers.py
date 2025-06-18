"""
Classification and analysis functions for research papers
"""

import re
import logging
from typing import Dict, List

from .config import MLOPS_KEYWORDS, TOOLS_PATTERNS

logger = logging.getLogger(__name__)


def extract_tools_from_text(text: str) -> List[str]:
    """Extract tools and technologies mentioned in text using regex patterns"""
    tools = []
    for pattern in TOOLS_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        tools.extend(matches)
    return list(set(tools))


def calculate_mlops_score(text: str) -> tuple[int, List[str]]:
    """Calculate MLOps relevance score and return relevant keywords"""
    text_lower = text.lower()
    mlops_score = 0
    relevant_keywords = []
    
    for keyword in MLOPS_KEYWORDS:
        if keyword.lower() in text_lower:
            mlops_score += 1
            relevant_keywords.append(keyword)
    
    return mlops_score, relevant_keywords


def generate_mlops_summary(text: str, relevant_keywords: List[str]) -> str:
    """Generate a summary explaining why a paper is MLOps relevant"""
    text_lower = text.lower()
    
    summary = f"This paper relates to MLOps/LLMOps/MLSystem Design because it mentions: {', '.join(relevant_keywords[:5])}. "
    
    if 'deployment' in text_lower or 'serving' in text_lower:
        summary += "It discusses model deployment and serving aspects. "
    if 'monitoring' in text_lower or 'observability' in text_lower:
        summary += "It covers monitoring and observability in ML systems. "
    if 'pipeline' in text_lower or 'workflow' in text_lower:
        summary += "It addresses ML pipeline and workflow management. "
    
    return summary


def classify_paper_mlops_relevance(paper: Dict) -> Dict:
    """Classify a single paper for MLOps relevance"""
    try:
        # Combine title and abstract for analysis
        text_content = f"{paper.get('title', '')} {paper.get('abstract', '')}"
        
        # Calculate MLOps relevance
        mlops_score, relevant_keywords = calculate_mlops_score(text_content)
        
        if not mlops_score == 0:
            return None
        
        # Generate MLOps summary
        summary_mlops = generate_mlops_summary(text_content, relevant_keywords)
        
        # Extract keywords (limit to top 10)
        keywords = list(set(relevant_keywords[:10]))
        
        # Extract tools and technologies
        tools = extract_tools_from_text(text_content)
        
        # Create processed paper object
        processed_paper = {
            'title': paper.get('title', ''),
            'authors': paper.get('authors', ''),
            'abstract': paper.get('abstract', ''),
            'url': paper.get('url', ''),
            'source': paper.get('source', ''),
            'summary_mlops': summary_mlops,
            'keywords': ', '.join(keywords),
            'tools': ', '.join(tools),
            'mlops_score': mlops_score
        }
        
        return processed_paper
        
    except Exception as e:
        logger.warning(f"Error processing paper: {e}")
        return None


def classify_papers_mlops_relevance(papers: List[Dict]) -> List[Dict]:
    """Classify papers for MLOps/LLMOps relevance and extract metadata"""
    logger.info("Classifying papers for MLOps relevance...")
    
    processed_papers = []
    
    for paper in papers:
        processed_paper = classify_paper_mlops_relevance(paper)
        if processed_paper:
            processed_papers.append(processed_paper)
    
    logger.info(f"Classified {len(processed_papers)} MLOps-relevant papers out of {len(papers)} total")
    return processed_papers 
