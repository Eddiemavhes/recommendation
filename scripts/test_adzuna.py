import requests
import json
from pprint import pprint

# API credentials
APP_ID = '394f4569'
API_KEY = 'b056e7a468781976de403fe611e052eb'

def test_adzuna_search(params, description):
    """Test Adzuna API with given parameters"""
    url = 'https://api.adzuna.com/v1/api/jobs/us/search/1'  # Changed to US market
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'User-Agent': 'JobMatcher/1.0'
    }
    
    # Add auth and format params
    params.update({
        'app_id': APP_ID,
        'app_key': API_KEY,
        'content-type': 'application/json',
        'what_and': params.get('what', '').split(),  # Split search terms for AND search
    })
    
    # Remove original 'what' parameter
    if 'what' in params:
        del params['what']
    
    print(f"\nTesting: {description}")
    print(f"URL: {url}")
    print(f"Parameters: {params}")
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.ok:
            data = response.json()
            print(f"Success! Found {data.get('count', 0)} results")
            if data.get('results'):
                print("\nFirst result:")
                pprint(data['results'][0])
        else:
            print(f"Error response: {response.text[:500]}")
            
    except Exception as e:
        print(f"Request failed: {e}")

def main():
    # Test different search combinations
    test_cases = [
        (
            {'what': 'software developer', 'results_per_page': 10},
            "Basic job search"
        ),
        (
            {'what': 'python developer', 'where': 'London', 'results_per_page': 10},
            "Location-based search"
        ),
        (
            {'what': 'software engineer', 'results_per_page': 10, 'salary_min': 30000, 'salary_max': 100000},
            "Search with salary range"
        ),
        (
            {'what': 'data scientist', 'results_per_page': 10, 'full_time': 1},
            "Full-time position search"
        )
    ]
    
    for params, description in test_cases:
        test_adzuna_search(params, description)

if __name__ == '__main__':
    main()
