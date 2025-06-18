#!/usr/bin/env python3
"""
Test script for paper parsing functionality using the new modular structure
"""

import sys
from pathlib import Path

# Add the project root and dags directory to the Python path
project_root = Path(__file__).parent.parent
dags_dir = project_root / "dags"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(dags_dir))

from src.parsers import parse_huggingface_papers, parse_all_arxiv_papers, combine_papers
from src.classifiers import classify_papers_mlops_relevance
from src.storage import save_raw_data, save_processed_data
from src.reports import generate_summary_report, generate_detailed_report
from src.utils import get_current_date_string, count_papers_by_source


def test_huggingface_parsing():
    """Test Hugging Face paper parsing"""
    print("Testing Hugging Face parsing...")
    
    try:
        papers = parse_huggingface_papers()
        print(f"✅ Successfully parsed {len(papers)} papers from Hugging Face")
        
        if papers:
            print("Sample paper:")
            sample = papers[0]
            print(f"  Title: {sample.get('title', 'N/A')}")
            print(f"  Authors: {sample.get('authors', 'N/A')[:100]}...")
            print(f"  Abstract: {sample.get('abstract', 'N/A')[:100]}...")
            print(f"  URL: {sample.get('url', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Hugging Face: {e}")
        return False


def test_arxiv_parsing():
    """Test ArXiv paper parsing"""
    print("\nTesting ArXiv parsing...")
    
    try:
        papers = parse_all_arxiv_papers()
        print(f"✅ Successfully parsed {len(papers)} papers from ArXiv")
        
        if papers:
            # Show source distribution
            source_counts = count_papers_by_source(papers)
            print(f"Papers by source: {source_counts}")
            
            print("Sample paper:")
            sample = papers[0]
            print(f"  Title: {sample.get('title', 'N/A')}")
            print(f"  Authors: {sample.get('authors', 'N/A')[:100]}...")
            print(f"  Source: {sample.get('source', 'N/A')}")
            print(f"  URL: {sample.get('url', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing ArXiv: {e}")
        return False


def test_paper_combination():
    """Test paper combination functionality"""
    print("\nTesting paper combination...")
    
    try:
        hf_papers = parse_huggingface_papers()
        arxiv_papers = parse_all_arxiv_papers()
        
        combined_papers = combine_papers(hf_papers, arxiv_papers)
        
        expected_count = len(hf_papers) + len(arxiv_papers)
        actual_count = len(combined_papers)
        
        if expected_count == actual_count:
            print(f"✅ Successfully combined papers: {actual_count} total")
            return True, combined_papers
        else:
            print(f"❌ Paper count mismatch: expected {expected_count}, got {actual_count}")
            return False, []
        
    except Exception as e:
        print(f"❌ Error testing paper combination: {e}")
        return False, []


def test_mlops_classification():
    """Test MLOps classification logic"""
    print("\nTesting MLOps classification...")
    
    # Sample papers for testing
    test_papers = [
        {
            'title': 'MLOps: Continuous Delivery for Machine Learning',
            'abstract': 'This paper discusses machine learning operations, model deployment, and continuous integration for ML systems.',
            'authors': 'Test Author',
            'url': 'https://example.com/1',
            'source': 'test'
        },
        {
            'title': 'Deep Learning for Computer Vision',
            'abstract': 'This paper presents a new neural network architecture for image classification using convolutional layers.',
            'authors': 'Another Author', 
            'url': 'https://example.com/2',
            'source': 'test'
        },
        {
            'title': 'Kubernetes-based Model Serving at Scale',
            'abstract': 'We present a system for serving machine learning models using Kubernetes orchestration and Docker containers.',
            'authors': 'MLOps Author',
            'url': 'https://example.com/3',
            'source': 'test'
        }
    ]
    
    try:
        classified_papers = classify_papers_mlops_relevance(test_papers)
        
        print(f"✅ Classified {len(classified_papers)} MLOps-relevant papers out of {len(test_papers)} total")
        
        for paper in classified_papers:
            print(f"\nPaper: {paper['title']}")
            print(f"  MLOps Score: {paper['mlops_score']}")
            print(f"  Keywords: {paper['keywords']}")
            print(f"  Tools: {paper['tools']}")
            print(f"  Summary: {paper['summary_mlops'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing MLOps classification: {e}")
        return False


def test_data_storage():
    """Test data storage functionality"""
    print("\nTesting data storage...")
    
    try:
        # Create sample data
        sample_papers = [
            {
                'title': 'Test Paper 1',
                'authors': 'Author 1, Author 2',
                'abstract': 'This is a test abstract about MLOps and deployment.',
                'url': 'https://example.com/1',
                'source': 'test'
            },
            {
                'title': 'Test Paper 2',
                'authors': 'Author 3, Author 4',
                'abstract': 'Another test abstract about machine learning operations.',
                'url': 'https://example.com/2',
                'source': 'test'
            }
        ]
        
        current_date = get_current_date_string()
        
        # Test raw data storage
        raw_file = save_raw_data(sample_papers, current_date)
        print(f"✅ Saved raw data to: {raw_file}")
        
        # Test processed data storage
        processed_papers = classify_papers_mlops_relevance(sample_papers)
        processed_file = save_processed_data(processed_papers, current_date)
        print(f"✅ Saved processed data to: {processed_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing data storage: {e}")
        return False


def test_report_generation():
    """Test report generation functionality"""
    print("\nTesting report generation...")
    
    try:
        current_date = get_current_date_string()
        
        # Generate summary report
        print("Generating summary report...")
        generate_summary_report(current_date)
        
        # Generate detailed report
        detailed_report = generate_detailed_report(current_date)
        print(f"✅ Generated detailed report: {detailed_report}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing report generation: {e}")
        return False


def run_full_pipeline_test():
    """Run a complete end-to-end test of the pipeline"""
    print("\n" + "="*50)
    print("RUNNING FULL PIPELINE TEST")
    print("="*50)
    
    try:
        # Step 1: Parse papers
        print("Step 1: Parsing papers from all sources...")
        hf_papers = parse_huggingface_papers()
        arxiv_papers = parse_all_arxiv_papers()
        all_papers = combine_papers(hf_papers, arxiv_papers)
        
        print(f"  - Hugging Face: {len(hf_papers)} papers")
        print(f"  - ArXiv: {len(arxiv_papers)} papers")
        print(f"  - Total: {len(all_papers)} papers")
        
        # Step 2: Save raw data
        print("\nStep 2: Saving raw data...")
        current_date = get_current_date_string()
        raw_file = save_raw_data(all_papers, current_date)
        print(f"  - Raw data saved to: {raw_file}")
        
        # Step 3: Classify papers
        print("\nStep 3: Classifying papers for MLOps relevance...")
        processed_papers = classify_papers_mlops_relevance(all_papers)
        print(f"  - Found {len(processed_papers)} MLOps-relevant papers")
        
        # Step 4: Save processed data
        print("\nStep 4: Saving processed data...")
        processed_file = save_processed_data(processed_papers, current_date)
        print(f"  - Processed data saved to: {processed_file}")
        
        # Step 5: Generate reports
        print("\nStep 5: Generating reports...")
        generate_summary_report(current_date)
        detailed_report = generate_detailed_report(current_date)
        
        print(f"\n✅ PIPELINE TEST COMPLETED SUCCESSFULLY!")
        print(f"   - Total papers processed: {len(all_papers)}")
        print(f"   - MLOps-relevant papers: {len(processed_papers)}")
        print(f"   - Success rate: {len(processed_papers)/len(all_papers)*100:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ PIPELINE TEST FAILED: {e}")
        return False


def main():
    """Run all tests"""
    print("=== Paper Parsing System Tests (Modular Version) ===")
    
    tests = [
        ("Hugging Face Parsing", test_huggingface_parsing),
        ("ArXiv Parsing", test_arxiv_parsing),
        ("MLOps Classification", test_mlops_classification),
        ("Data Storage", test_data_storage),
        ("Report Generation", test_report_generation),
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
    
    # Run full pipeline test
    print(f"\n{'-'*50}")
    print("Running: Full Pipeline Test")
    print(f"{'-'*50}")
    pipeline_result = run_full_pipeline_test()
    results.append(("Full Pipeline", pipeline_result))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:30} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! The refactored system is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")


if __name__ == "__main__":
    main() 
