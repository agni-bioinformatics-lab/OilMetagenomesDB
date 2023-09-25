# OilMetagenomesDB - Samples Column Specifications

This page describes columns definitions for all sample-level lists. Also there is a dictionary that describes materials column.

## Sample columns:

| Feature | Description | Example | Possible values | Type, pattern, enum |
| :---: | :---: | :---: | :---: | :---: |
| project_name | Name of the project, <br> AuthorYear format | Zilov2023 | article_common | "type": "string", <br> "pattern": "\^[A-Z][a-z]+\\\d{4}$" |
| publication_year | Year of publication, <br> YYYY format | 2023 | article_common | "type": "string", <br> "pattern": "^(19[0-9]{2}\|20[0-2][0-9]\|2023)$" |
| publication_doi | DOI of the article | 10.1007/s00253-018-8766-2 | article_common | "type": "string", <br> "pattern": "^10\\\\.\\\d{4,9}\\\\/[^,]+$" |
| oil_reservoir | The name of the oil field should be written in the article or found by coordinates | romashkinskoe | db_common | "type": "string", <br> "pattern": "^(?!\\\s*$).*\|None\|unknown\$" |
| oil_wells | The ID of the well in the article | A1 | db_common | "type": "string", <br> "pattern": "^.+$" |
| latitude | The latitude at which the sample was taken | 1000.0 | db_common | "type": "string", <br> "pattern": "^(-?)(\\\d+\\\\.\\\d+\|None\|unknown)$" |
| longitude | The longitude at which the sample was taken | 1000.0 | db_common | "type": "string", <br> "pattern": "^(-?)(\\\d+\\\\.\\\d+\|None\|unknown)$" |
| geo_loc_name | The country where the well/field is located, from where samples were taken for analysis | usa | db_common | Specified in an enum <br> [(link)](https://github.com/agni-bioinformatics-lab/OilMetagenomesDB/blob/main/schemas_samples/geo_loc_name.json) |
| study_primary_focus | The focus of the research in the article | ecology | article_common | Specified in an enum <br> [(link)](https://github.com/agni-bioinformatics-lab/OilMetagenomesDB/blob/main/schemas_samples/study_primary_focus.json) |
| study_process | The biochemical process that is studied in the article | bioremediation | article_common | Specified in an enum <br> [(link)](https://github.com/agni-bioinformatics-lab/OilMetagenomesDB/blob/main/schemas_samples/study_process.json) |
| depth | Sampling depth in meters | 1000.0 | db_common | "type": "string", <br> "pattern": "^(\\\d+\\\\.\\\d+\|None\|unknown)$" |
| temp | Temperature in Celsius | 100.0 | db_common | "type": "string", <br> "pattern": "^(\\\d+\\\\.\\\d+\|None\|unknown)$" |
| pH | Sample acidity | 10.0 | db_common | "type": "string", <br> "pattern": "^(\\\d+\\\\.\\\d+\|None\|unknown)$" |
| salinity | Specify in ppt, if 10% is specified, write 100; <br> 1 ppt = 1000 mg/l | 0.5 | db_common | "type": "string", <br> "pattern": "^(\\\d+\\\\.\\\d+\|None\|unknown)$" |
| API | Specify in API units. <br> For example: 0.932 g/cm3 = 932 kg/m3 = 20 API | 20 | Unique to the article | "type": "string", <br> "pattern": "^(\\\d+\|None\|unknown)$" |
| NO3- | We specify in mg/l | 5.0 | db_common | "type": "string", <br> "pattern": "^(\\\d+\\\\.\\\d+\|None\|unknown)$" |
| PO43- | We specify in mg/l | 5.0 | db_common | "type": "string", <br> "pattern": "^(\\\d+\\\\.\\\d+\|None\|unknown)$" |
| SO42- | We specify in mg/l | 5.0 | db_common | "type": "string", <br> "pattern": "^(\\\d+\\\\.\\\d+\|None\|unknown)$" |
| Ca2+ | We specify in mg/l | 5.0 | db_common | "type": "string", <br> "pattern": "^(\\\d+\\\\.\\\d+\|None\|unknown)$" |
| Mg2+ | We specify in mg/l | 5.0 | db_common | "type": "string", <br> "pattern": "^(\\\d+\\\\.\\\d+\|None\|unknown)$" |
| Na+ | We specify in mg/l | 5.0 | db_common | "type": "string", <br> "pattern": "^(\\\d+\\\\.\\\d+\|None\|unknown)$" |
| K+ | We specify in mg/l | 5.0 | db_common | "type": "string", <br> "pattern": "^(\\\d+\\\\.\\\d+\|None\|unknown)$" |
| Cl- | We specify in mg/l | 5.0 | db_common | "type": "string", <br> "pattern": "^(\\\d+\\\\.\\\d+\|None\|unknown)$" |
| HCO3- | We specify in mg/l | 5.0 | db_common | "type": "string", <br> "pattern": "^(\\\d+\\\\.\\\d+\|None\|unknown)$" |
| acetate | We specify in mg/l | 5.0 | db_common | "type": "string", <br> "pattern": "^(\\\d+\\\\.\\\d+\|None\|unknown)$" |
| sample_name | What kind of ID was used by the study for this sample. <br> We take it from the article. If not in the article, we take it from NCBI | a1 | article_uniq | "type": "string", <br> "pattern": "^.+$" |
| feature | Description of the medium from which the sample was obtained | littoral zone | db_common | Specified in an enum <br> [(link)](https://github.com/agni-bioinformatics-lab/OilMetagenomesDB/blob/main/schemas_samples/feature.json) |
| material | The type of sample from which bacterial dna was isolated | crude oil | db_common | Specified in an enum <br> [(link)](https://github.com/agni-bioinformatics-lab/OilMetagenomesDB/blob/main/schemas_samples/material.json) |
| collection_date | Date of sample collection | 2020 | db_common | "type": "string", <br> "pattern": "^(\\\d+\|None\|unknown)$" |
| archive | The archive where the library data is stored | SRA | article_common | Specified in an enum <br> [(link)](https://github.com/agni-bioinformatics-lab/OilMetagenomesDB/blob/main/schemas_samples/archive.json) |
| archive_project | Project code with all sample data (PRJ). The article may specify the code of a set of experiments (SRP), experiment code (SRX), sample code (SRS). <br> Through these designations in NCBI, you can find the project code | PRJNA604781 | article_common | "type": "string", <br> "pattern": "^(PRJ\|SRP\|SRX\|SRS)[A-Z]*\\\d+$" |
| archive_accession | Data code for sample, <br> starts SRS for SRA or ERS for ENA | SRS5536770 | db_uniq | "type": "string", <br> "pattern": "^(SRS\|ERS)\\\d+$" |


## Dictionary for Materials Column:

**seawater** - often taken from oil spills

**production fluid** - the undivided oil production fluid that has not yet separated

**formation water** - water that is together with oil and solid phase, but which contains very little oil

**injection water** - water that is pumped in to pump out oil under pressure

**oil contaminated soil** - soil contaminated with oil

**soil** - just soil without oil, control

**crude oil** - pure oil, high percentage of hydrocarbons

**core** - a cylindrical rock sample that is extracted from a well for laboratory analysis

**reservoir fluids** - same as reservoir brine, may be what is produced but also called in an oil reservoir, a mixture of water, oil and solids, not yet stratified

**drilling mud** - is what's needed to lubricate the drill

**drilling cuttings** - cuttings that go back to the ground when drilling

**oil sands** - refers to a type of unconventional petroleum deposit that consists of a mixture of sand, water, clay, and bitumen, often refers to surface mining

**clean water** - often the control of any water

**solid** - solid phase formed after extraction

**grounded water** - underground water that has little connection to the reservoir itself

**pipeline solids** - sediment on the pipeline, usually taken to check for corrosion.
