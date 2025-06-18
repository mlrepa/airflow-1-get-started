"""
Web scraping and parsing functions for research papers
"""

import logging
import time
from typing import Dict, List
import requests
from bs4 import BeautifulSoup

from .config import DATA_SOURCES, DEFAULT_HEADERS, MAX_PAPERS_PER_SOURCE, REQUEST_TIMEOUT, ARXIV_REQUEST_DELAY

logger = logging.getLogger(__name__)


def get_huggingface_abstract(paper_url: str) -> str:
    """Fetch abstract from individual HuggingFace paper page"""
    try:
        # Add small delay to be respectful to HuggingFace servers
        time.sleep(ARXIV_REQUEST_DELAY)  # Reuse the same delay setting
        
        response = requests.get(paper_url, headers=DEFAULT_HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Method 1: Look for Abstract heading followed by content
        abstract_heading = soup.find('h2', string=lambda text: text and 'abstract' in text.lower())
        if abstract_heading:
            # Find the next div or section containing the abstract
            abstract_container = abstract_heading.find_next_sibling('div')
            if abstract_container:
                # Look for the main abstract paragraph (skip AI-generated summary)
                abstract_paragraphs = abstract_container.find_all('p')
                for p in abstract_paragraphs:
                    # Skip AI-generated summary (usually has specific styling)
                    if 'text-gray-600' in p.get('class', []) or 'text-gray-700' in p.get('class', []):
                        abstract_text = p.get_text(strip=True)
                        if abstract_text and len(abstract_text) > 100:  # Ensure it's substantial
                            logger.debug(f"Found abstract via Abstract heading for {paper_url}")
                            return abstract_text
        
        # Method 2: Look for the main content area with abstract
        main_content = soup.find('div', class_='pb-8')
        if main_content:
            # Look for paragraphs that contain substantial text
            paragraphs = main_content.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                # Look for paragraphs that seem like abstracts (long, academic content)
                if (text and len(text) > 200 and 
                    any(word in text.lower() for word in ['research', 'study', 'propose', 'method', 'approach', 'investigate', 'present', 'analysis'])):
                    logger.debug(f"Found abstract via main content for {paper_url}")
                    return text
        
        # Method 3: Look for any substantial paragraph content
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            if text and len(text) > 300:  # Very substantial text
                # Check if it looks like an abstract (not navigation, not metadata)
                if not any(skip_word in text.lower() for skip_word in ['click', 'download', 'github', 'hugging face', 'sign in', 'join']):
                    logger.debug(f"Found abstract via substantial paragraph for {paper_url}")
                    return text
        
        logger.warning(f"Could not find abstract for {paper_url}")
        return ""
        
    except Exception as e:
        logger.warning(f"Error fetching abstract from {paper_url}: {e}")
        return ""


def parse_huggingface_papers() -> List[Dict]:
    """Parse papers from Hugging Face daily papers page"""
    logger.info("Parsing Hugging Face papers...")
    
    try:
        response = requests.get(
            DATA_SOURCES["huggingface"], 
            headers=DEFAULT_HEADERS, 
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        papers = []
        
        # Find paper containers
        paper_elements = soup.find_all('div', class_='paper-item') or soup.find_all('article')
        
        for element in paper_elements[:MAX_PAPERS_PER_SOURCE]:
            try:
                title_elem = element.find('h3') or element.find('h2') or element.find('a')
                if not title_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                
                # Try to find authors
                authors_elem = element.find('div', class_='authors') or element.find('p')
                authors = authors_elem.get_text(strip=True) if authors_elem else "Unknown"
                
                # Try to find link
                link_elem = element.find('a', href=True)
                url = link_elem['href'] if link_elem else ""
                if url and not url.startswith('http'):
                    url = f"https://huggingface.co{url}"
                
                # Get abstract from the individual paper page
                abstract = ""
                if url and url != DATA_SOURCES["huggingface"]:
                    abstract = get_huggingface_abstract(url)
                
                # Fallback: try to get description from the list page if individual page fails
                if not abstract:
                    desc_elem = element.find('div', class_='abstract') or element.find('p')
                    if desc_elem:
                        abstract = desc_elem.get_text(strip=True)
                
                if title:
                    papers.append({
                        'source': 'huggingface',
                        'title': title,
                        'authors': authors,
                        'abstract': abstract,
                        'url': url or DATA_SOURCES["huggingface"]
                    })
                    
            except Exception as e:
                logger.warning(f"Error parsing HF paper element: {e}")
                continue
        
        logger.info(f"Parsed {len(papers)} papers from Hugging Face")
        return papers
        
    except Exception as e:
        logger.error(f"Error parsing Hugging Face: {e}")
        return []


def get_arxiv_abstract(paper_url: str) -> str:
    """Fetch abstract from individual ArXiv paper page"""
    try:
        # Add small delay to be respectful to ArXiv servers
        time.sleep(ARXIV_REQUEST_DELAY)
        
        response = requests.get(paper_url, headers=DEFAULT_HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to find abstract from og:description meta tag first (most reliable)
        og_description = soup.find('meta', property='og:description')
        if og_description and og_description.get('content'):
            abstract = og_description['content'].strip()
            if abstract and len(abstract) > 50:  # Ensure it's a meaningful abstract
                logger.debug(f"Found abstract via og:description for {paper_url}")
                return abstract
        
        # Fallback: try to find abstract from the abstract blockquote
        abstract_elem = soup.find('blockquote', class_='abstract')
        if abstract_elem:
            # Remove the "Abstract:" label if present
            abstract_text = abstract_elem.get_text(strip=True)
            if abstract_text.startswith('Abstract:'):
                abstract_text = abstract_text[9:].strip()
            if abstract_text:
                logger.debug(f"Found abstract via blockquote.abstract for {paper_url}")
                return abstract_text
        
        # Second fallback: look for any blockquote (sometimes abstract is in a generic blockquote)
        blockquote = soup.find('blockquote')
        if blockquote:
            abstract_text = blockquote.get_text(strip=True)
            if abstract_text.startswith('Abstract:'):
                abstract_text = abstract_text[9:].strip()
            if abstract_text and len(abstract_text) > 50:
                logger.debug(f"Found abstract via generic blockquote for {paper_url}")
                return abstract_text
        
        logger.warning(f"Could not find abstract for {paper_url}")
        return ""
        
    except Exception as e:
        logger.warning(f"Error fetching abstract from {paper_url}: {e}")
        return ""


def parse_arxiv_category(category: str, url: str) -> List[Dict]:
    """Parse papers from a specific ArXiv category"""
    logger.info(f"Parsing ArXiv category: {category}")
    
    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        papers = []
        
        # Find paper entries in ArXiv format
        paper_elements = soup.find_all('dt')[:MAX_PAPERS_PER_SOURCE]
        
        for dt_element in paper_elements:
            try:
                # Get ArXiv ID and URL
                link = dt_element.find('a', href=True)
                if not link:
                    continue
                    
                arxiv_id = link.get_text(strip=True).replace('arXiv:', '')
                paper_url = f"https://arxiv.org/abs/{arxiv_id}"
                
                # Find corresponding dd element with paper details
                dd_element = dt_element.find_next_sibling('dd')
                if not dd_element:
                    continue
                
                # Get title
                title_elem = dd_element.find('div', class_='list-title')
                title = ""
                if title_elem:
                    title = title_elem.get_text().replace('Title:', '').strip()
                
                # Get authors
                authors_elem = dd_element.find('div', class_='list-authors')
                authors = ""
                if authors_elem:
                    authors = authors_elem.get_text().replace('Authors:', '').strip()
                
                # Get abstract from the individual paper page
                abstract = get_arxiv_abstract(paper_url)
                
                # Fallback: try to get abstract from the list page if individual page fails
                if not abstract:
                    abstract_elem = dd_element.find('p', class_='mathjax')
                    if abstract_elem:
                        abstract = abstract_elem.get_text(strip=True)
                
                if title:
                    papers.append({
                        'source': category,
                        'title': title,
                        'authors': authors,
                        'abstract': abstract,
                        'url': paper_url
                    })
                    
            except Exception as e:
                logger.warning(f"Error parsing ArXiv paper: {e}")
                continue
        
        logger.info(f"Parsed {len(papers)} papers from {category}")
        return papers
        
    except Exception as e:
        logger.error(f"Error parsing ArXiv {category}: {e}")
        return []


def parse_all_arxiv_papers() -> List[Dict]:
    """Parse papers from all ArXiv categories"""
    all_papers = []
    
    for category, url in DATA_SOURCES.items():
        if category == 'huggingface':
            continue
        
        papers = parse_arxiv_category(category, url)
        all_papers.extend(papers)
    
    logger.info(f"Total ArXiv papers parsed: {len(all_papers)}")
    return all_papers


def combine_papers(hf_papers: List[Dict], arxiv_papers: List[Dict]) -> List[Dict]:
    """Combine papers from all sources"""
    all_papers = hf_papers + arxiv_papers
    logger.info(f"Total papers collected: {len(all_papers)}")
    return all_papers 
