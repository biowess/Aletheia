import requests
res = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi", params={"db": "pubmed", "id": "35544710", "retmode": "xml"})
print(res.text[:2000])
