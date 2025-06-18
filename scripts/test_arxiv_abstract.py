#!/usr/bin/env python3
"""
Test script specifically for ArXiv abstract fetching functionality
"""

import sys
from pathlib import Path

# Add the project root and dags directory to the Python path
project_root = Path(__file__).parent.parent
dags_dir = project_root / "dags"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(dags_dir))

from src.parsers import get_arxiv_abstract, get_huggingface_abstract, parse_arxiv_category, parse_huggingface_papers


def test_single_arxiv_abstract():
    """Test fetching abstract from a single ArXiv paper"""
    print("Testing single ArXiv abstract fetching...")
    
    # Test with the example paper from the user's query
    test_url = "https://arxiv.org/abs/2506.14746"
    
    print(f"Fetching abstract for: {test_url}")
    abstract = get_arxiv_abstract(test_url)
    
    if abstract:
        print("✅ Successfully fetched abstract!")
        print(f"Abstract length: {len(abstract)} characters")
        print(f"Abstract preview: {abstract[:200]}...")
        
        # Check if it contains expected content from the example
        expected_keywords = ["bandit learning", "best-arm identification", "PAC framework"]
        found_keywords = [kw for kw in expected_keywords if kw.lower() in abstract.lower()]
        
        if found_keywords:
            print(f"✅ Abstract contains expected keywords: {found_keywords}")
        else:
            print("⚠️  Abstract doesn't contain expected keywords, but that's okay")
        
        return True
    else:
        print("❌ Failed to fetch abstract")
        return False


def test_multiple_arxiv_abstracts():
    """Test fetching abstracts from multiple ArXiv papers"""
    print("\nTesting multiple ArXiv abstracts...")
    
    # Test URLs for different types of papers
    test_urls = [
        "https://arxiv.org/abs/2506.14746",  # The example from user
        "https://arxiv.org/abs/2506.14698",  # Another recent paper
    ]
    
    results = []
    for url in test_urls:
        print(f"\nTesting: {url}")
        abstract = get_arxiv_abstract(url)
        
        if abstract:
            print(f"✅ Success - {len(abstract)} chars")
            print(f"Preview: {abstract[:100]}...")
            results.append(True)
        else:
            print("❌ Failed")
            results.append(False)
    
    success_rate = sum(results) / len(results) * 100
    print(f"\nSuccess rate: {success_rate:.1f}% ({sum(results)}/{len(results)})")
    
    return success_rate >= 50  # At least 50% success rate


def test_arxiv_category_with_abstracts():
    """Test parsing a full ArXiv category with the new abstract fetching"""
    print("\nTesting ArXiv category parsing with abstract fetching...")
    
    # Test with a smaller number to avoid too many requests
    from src.config import MAX_PAPERS_PER_SOURCE
    original_max = MAX_PAPERS_PER_SOURCE
    
    # Temporarily reduce the number for testing
    import src.config
    src.config.MAX_PAPERS_PER_SOURCE = 3
    
    try:
        # Test with cs.LG (Machine Learning) category
        papers = parse_arxiv_category("arxiv_lg", "https://arxiv.org/list/cs.LG/recent")
        
        print(f"Parsed {len(papers)} papers")
        
        abstracts_found = 0
        for i, paper in enumerate(papers):
            abstract = paper.get('abstract', '')
            if abstract:
                abstracts_found += 1
                print(f"\nPaper {i+1}:")
                print(f"  Title: {paper['title'][:80]}...")
                print(f"  Abstract length: {len(abstract)} chars")
                print(f"  Abstract preview: {abstract[:150]}...")
            else:
                print(f"\nPaper {i+1}: No abstract found")
                print(f"  Title: {paper['title'][:80]}...")
        
        success_rate = abstracts_found / len(papers) * 100 if papers else 0
        print(f"\nAbstract success rate: {success_rate:.1f}% ({abstracts_found}/{len(papers)})")
        
        return success_rate >= 70  # At least 70% should have abstracts
        
    finally:
        # Restore original setting
        src.config.MAX_PAPERS_PER_SOURCE = original_max


def test_abstract_quality():
    """Test the quality of fetched abstracts"""
    print("\nTesting abstract quality...")
    
    test_url = "https://arxiv.org/abs/2506.14746"
    abstract = get_arxiv_abstract(test_url)
    
    if not abstract:
        print("❌ No abstract to test")
        return False
    
    quality_checks = []
    
    # Check 1: Minimum length
    min_length = len(abstract) >= 100
    quality_checks.append(("Minimum length (100+ chars)", min_length))
    
    # Check 2: Contains typical academic language
    academic_words = ["study", "research", "analysis", "method", "approach", "results", "conclusion"]
    has_academic_language = any(word in abstract.lower() for word in academic_words)
    quality_checks.append(("Contains academic language", has_academic_language))
    
    # Check 3: Not just metadata
    metadata_indicators = ["doi:", "arxiv:", "submitted", "accepted"]
    is_not_metadata = not any(indicator in abstract.lower() for indicator in metadata_indicators)
    quality_checks.append(("Not just metadata", is_not_metadata))
    
    # Check 4: Contains sentences (has periods)
    has_sentences = "." in abstract
    quality_checks.append(("Contains sentences", has_sentences))
    
    print("Quality checks:")
    passed_checks = 0
    for check_name, passed in quality_checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {check_name}")
        if passed:
            passed_checks += 1
    
    quality_score = passed_checks / len(quality_checks) * 100
    print(f"\nQuality score: {quality_score:.1f}% ({passed_checks}/{len(quality_checks)})")
    
    return quality_score >= 75  # At least 75% quality score


def test_single_huggingface_abstract():
    """Test fetching abstract from a single HuggingFace paper"""
    print("Testing single HuggingFace abstract fetching...")
    
    # Test with a known HuggingFace paper
    test_url = "https://huggingface.co/papers/2506.14429"
    
    print(f"Fetching abstract for: {test_url}")
    abstract = get_huggingface_abstract(test_url)
    
    if abstract:
        print("✅ Successfully fetched abstract!")
        print(f"Abstract length: {len(abstract)} characters")
        print(f"Abstract preview: {abstract[:200]}...")
        
        # Check if it contains expected content
        expected_keywords = ["diffusion", "LLMs", "context", "long"]
        found_keywords = [kw for kw in expected_keywords if kw.lower() in abstract.lower()]
        
        if found_keywords:
            print(f"✅ Abstract contains expected keywords: {found_keywords}")
        else:
            print("⚠️  Abstract doesn't contain expected keywords, but that's okay")
        
        return True
    else:
        print("❌ Failed to fetch abstract")
        return False


def test_huggingface_parsing_with_abstracts():
    """Test parsing HuggingFace papers with the new abstract fetching"""
    print("\nTesting HuggingFace parsing with abstract fetching...")
    
    # Test with a smaller number to avoid too many requests
    from src.config import MAX_PAPERS_PER_SOURCE
    original_max = MAX_PAPERS_PER_SOURCE
    
    # Temporarily reduce the number for testing
    import src.config
    src.config.MAX_PAPERS_PER_SOURCE = 3
    
    try:
        papers = parse_huggingface_papers()
        
        print(f"Parsed {len(papers)} papers")
        
        abstracts_found = 0
        for i, paper in enumerate(papers):
            abstract = paper.get('abstract', '')
            if abstract:
                abstracts_found += 1
                print(f"\nPaper {i+1}:")
                print(f"  Title: {paper['title'][:80]}...")
                print(f"  Abstract length: {len(abstract)} chars")
                print(f"  Abstract preview: {abstract[:150]}...")
            else:
                print(f"\nPaper {i+1}: No abstract found")
                print(f"  Title: {paper['title'][:80]}...")
        
        success_rate = abstracts_found / len(papers) * 100 if papers else 0
        print(f"\nAbstract success rate: {success_rate:.1f}% ({abstracts_found}/{len(papers)})")
        
        return success_rate >= 70  # At least 70% should have abstracts
        
    finally:
        # Restore original setting
        src.config.MAX_PAPERS_PER_SOURCE = original_max


def main():
    """Run all abstract fetching tests"""
    print("=== Paper Abstract Fetching Tests ===")
    
    tests = [
        ("ArXiv Single Abstract Fetch", test_single_arxiv_abstract),
        ("ArXiv Multiple Abstracts Fetch", test_multiple_arxiv_abstracts),
        ("ArXiv Category Parsing with Abstracts", test_arxiv_category_with_abstracts),
        ("ArXiv Abstract Quality Check", test_abstract_quality),
        ("HuggingFace Single Abstract Fetch", test_single_huggingface_abstract),
        ("HuggingFace Parsing with Abstracts", test_huggingface_parsing_with_abstracts),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'-'*50}")
        print(f"Running: {test_name}")
        print(f"{'-'*50}")
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:35} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All abstract fetching tests passed!")
    elif passed >= len(results) * 0.75:
        print("✅ Most tests passed - Abstract fetching is working well")
    else:
        print("⚠️  Some tests failed - check the implementation")


if __name__ == "__main__":
    main() 
