#!/usr/bin/env python3
"""
Test script for report saving functionality
"""

import json
import sys
from pathlib import Path

# Add the project root and dags directory to the Python path
project_root = Path(__file__).parent.parent
dags_dir = project_root / "dags"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(dags_dir))

from datetime import datetime
from src.reports import save_summary_report, save_detailed_markdown_report, generate_detailed_report
from src.storage import save_processed_data


def get_current_date_string() -> str:
    """Get current date in YYYY-MM-DD format"""
    return datetime.now().strftime('%Y-%m-%d')


def create_test_data():
    """Create some test processed papers data"""
    test_date = get_current_date_string()
    
    # Sample processed papers
    test_papers = [
        {
            'title': 'MLOps Best Practices for Production Systems',
            'authors': 'John Doe, Jane Smith',
            'abstract': 'This paper discusses machine learning operations, model deployment, and continuous integration for ML systems.',
            'url': 'https://example.com/1',
            'source': 'test_source',
            'summary_mlops': 'This paper relates to MLOps because it mentions deployment and CI/CD.',
            'keywords': 'mlops, deployment, ci/cd',
            'tools': 'Docker, Kubernetes, MLflow',
            'mlops_score': 5
        },
        {
            'title': 'Kubernetes-based Model Serving at Scale',
            'authors': 'Bob Johnson',
            'abstract': 'We present a system for serving machine learning models using Kubernetes orchestration.',
            'url': 'https://example.com/2',
            'source': 'arxiv_lg',
            'summary_mlops': 'This paper relates to MLOps because it mentions Kubernetes and model serving.',
            'keywords': 'kubernetes, model serving, orchestration',
            'tools': 'Kubernetes, Docker',
            'mlops_score': 4
        },
        {
            'title': 'Monitoring ML Models in Production',
            'authors': 'Alice Brown, Charlie Wilson',
            'abstract': 'This study investigates monitoring approaches for machine learning models deployed in production environments.',
            'url': 'https://example.com/3',
            'source': 'huggingface',
            'summary_mlops': 'This paper relates to MLOps because it discusses monitoring and production deployment.',
            'keywords': 'monitoring, production, observability',
            'tools': 'Prometheus, Grafana',
            'mlops_score': 3
        }
    ]
    
    # Save test data
    save_processed_data(test_papers, test_date)
    return test_date


def test_json_report_saving():
    """Test saving JSON summary report"""
    print("Testing JSON report saving...")
    
    try:
        test_date = create_test_data()
        
        # Save JSON report
        report_file = save_summary_report(test_date)
        
        if report_file and Path(report_file).exists():
            print(f"✅ JSON report saved successfully: {report_file}")
            
            # Verify content
            with open(report_file, 'r') as f:
                report_data = json.load(f)
            
            print(f"  - Date: {report_data.get('date')}")
            print(f"  - Total papers: {report_data.get('total_papers')}")
            print(f"  - Average MLOps score: {report_data.get('avg_mlops_score'):.2f}")
            print(f"  - Sources: {report_data.get('sources')}")
            print(f"  - Top tools: {report_data.get('top_tools')[:3]}")
            
            return True
        else:
            print("❌ Failed to save JSON report")
            return False
            
    except Exception as e:
        print(f"❌ Error testing JSON report: {e}")
        return False


def test_markdown_report_saving():
    """Test saving Markdown summary report"""
    print("\nTesting Markdown report saving...")
    
    try:
        test_date = get_current_date_string()
        
        # Save Markdown report
        report_file = save_detailed_markdown_report(test_date)
        
        if report_file and Path(report_file).exists():
            print(f"✅ Markdown report saved successfully: {report_file}")
            
            # Verify content
            with open(report_file, 'r') as f:
                content = f.read()
            
            print(f"  - Content length: {len(content)} characters")
            print("  - Content preview:")
            print("    " + "\n    ".join(content.split('\n')[:10]))
            
            # Check for expected sections
            expected_sections = ["# Daily Papers Summary Report", "## Overview", "## Papers by Source", "## Top Mentioned Tools", "## Sample Paper Titles"]
            found_sections = [section for section in expected_sections if section in content]
            
            print(f"  - Found sections: {len(found_sections)}/{len(expected_sections)}")
            
            return len(found_sections) >= 4
        else:
            print("❌ Failed to save Markdown report")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Markdown report: {e}")
        return False


def test_detailed_report_generation():
    """Test detailed report generation"""
    print("\nTesting detailed report generation...")
    
    try:
        test_date = get_current_date_string()
        
        # Generate detailed report
        report_data = generate_detailed_report(test_date)
        
        print("✅ Detailed report generated successfully")
        print(f"  - Date: {report_data.get('date')}")
        print(f"  - Total papers: {report_data.get('total_papers')}")
        print(f"  - Average MLOps score: {report_data.get('avg_mlops_score'):.2f}")
        print(f"  - Sources: {report_data.get('sources')}")
        print(f"  - Number of top tools: {len(report_data.get('top_tools', []))}")
        print(f"  - Number of sample titles: {len(report_data.get('sample_titles', []))}")
        
        # Validate structure
        required_keys = ['date', 'total_papers', 'sources', 'top_tools', 'sample_titles', 'avg_mlops_score']
        missing_keys = [key for key in required_keys if key not in report_data]
        
        if not missing_keys:
            print("  ✅ All required keys present")
            return True
        else:
            print(f"  ❌ Missing keys: {missing_keys}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing detailed report generation: {e}")
        return False


def test_reports_directory_structure():
    """Test that reports directory is created correctly"""
    print("\nTesting reports directory structure...")
    
    try:
        test_date = get_current_date_string()
        
        # Save both types of reports
        json_file = save_summary_report(test_date)
        markdown_file = save_detailed_markdown_report(test_date)
        
        reports_dir = Path("data/reports")
        
        if reports_dir.exists() and reports_dir.is_dir():
            print("✅ Reports directory created successfully")
            
            # List files in directory
            report_files = list(reports_dir.glob("*"))
            print(f"  - Files in reports directory: {len(report_files)}")
            
            for file in report_files:
                print(f"    - {file.name} ({file.stat().st_size} bytes)")
            
            # Check if both files exist
            json_exists = any(f.name.endswith('.json') for f in report_files)
            markdown_exists = any(f.name.endswith('.md') for f in report_files)
            
            if json_exists and markdown_exists:
                print("  ✅ Both JSON and Markdown reports found")
                return True
            else:
                print(f"  ❌ Missing files - JSON: {json_exists}, Markdown: {markdown_exists}")
                return False
        else:
            print("❌ Reports directory not created")
            return False
            
    except Exception as e:
        print(f"❌ Error testing directory structure: {e}")
        return False


def cleanup_test_files():
    """Clean up test files"""
    try:
        # Remove test files
        reports_dir = Path("data/reports")
        if reports_dir.exists():
            for file in reports_dir.glob("*"):
                file.unlink()
            print("🧹 Cleaned up test files")
    except Exception as e:
        print(f"⚠️  Error cleaning up: {e}")


def main():
    """Run all report saving tests"""
    print("=== Report Saving Tests ===")
    
    tests = [
        ("Detailed Report Generation", test_detailed_report_generation),
        ("JSON Report Saving", test_json_report_saving),
        ("Markdown Report Saving", test_markdown_report_saving),
        ("Reports Directory Structure", test_reports_directory_structure),
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
        print("🎉 All report saving tests passed!")
    elif passed >= len(results) * 0.75:
        print("✅ Most tests passed - Report saving is working well")
    else:
        print("⚠️  Some tests failed - check the implementation")
    
    # Cleanup
    cleanup_test_files()


if __name__ == "__main__":
    main() 
