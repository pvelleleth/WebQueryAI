import requests

def test_query_webpage():
    url = "http://localhost:8000/query_webpage_rag/"
    test_data = {
        "url": "https://www.papowerswitch.com/shop-for-rates-results/?zipcode=19050&serviceType=residential&distributor=1182&distributorrate=R+-+Regular+Residential+Service",
        "query": "Which supplier has the cheapest rate and what is the estimated monthly cost for it?"
    }
    
    response = requests.post(url, json=test_data)
    
    if response.status_code == 200:
        print("Test passed!")
        print("Response:", response.json())
    else:
        print("Test failed!")
        print("Status Code:", response.status_code)
        print("Response:", response.text)

if __name__ == "__main__":
    test_query_webpage()
