from services.wikimedia_search_service import (
    WikimediaSearchService
)

service = (
    WikimediaSearchService()
)

queries = [
    "Curacao football team",
    "Germany national football team",
    "football stadium crowd",
    "football goal celebration"
]

for query in queries:

    result = service.search(
        query
    )

    print("\n==========")
    print(query)
    print(result["title"])
    print(result["asset_url"])