from Bio import UniProt

# Search for reviewed SARS-CoV-2 proteins
query = "(organism_id:2697049) AND (reviewed:true)"
results = list(UniProt.search(query))

print(f"Found {len(results)} proteins")
for result in results[:5]:
    print(f"{result['primaryAccession']}: "
          f"{result['proteinDescription']['recommendedName']['fullName']['value']}")


query = "(organism_id:2697049) AND (reviewed:true)"
results = UniProt.search(query)

    # Iterate over results
for protein in results:
    accession = protein['primaryAccession']
    organism = protein.get('organism', {}).get('scientificName', 'Unknown')
    print(f"{accession}: {organism}")