<h2 align="center">Instructions for adding data to the common_samples and common_libraries tables</h2> 

> Requirements:
> - the study must be from published sources;
> - sequencing data must be published on NCBI.

Order of Action:
1) Find the NCBI bioproject identifier in the article (e.g. PRJNA729662)

2) Download the parsing script **parse_bioproject.py** from the [OilMetagenomesDB](https://github.com/agni-bioinformatics-lab/OilMetagenomesDB) repository

3) Navigate in the console to the folder where your script is located

4) Use the **parse_bioproject.py** script to collect metadata from NCBI
```ruby
   python parse_bioproject.py -id PRJNA729662
```
5) In the folder with your script there should be a tsv file with all metadata on the bioproject with NCBI. This data will be needed to fill in the final tables *common_samples* and *common_libraries*

![Image alt](/assets/image/instructions/metadata.png)

6) Go to excel or google tables to generate the tables *common_samples* and *common_libraries*

7) Open the tsv output file in google spreadsheets or excel

![Image alt](/assets/image/instructions/google.png)

8) Generate columns for tables *common_samples* and *common_libraries* on separate sheets in google tables. You can copy the list of column names below

For the *common_samples* table

project_name | publication_year | publication_doi |oil_reservoir | oil_wells | latitude | longitude | geo_loc_name | study_primary_focus | study_process | depth |temp | pH | salinity | API | NO3<sup>-</sup>| PO<sub>4</sub><sup>3-</sup> | SO<sub>4</sub><sup>2-</sup>  | Ca<sup>2+</sup> | Mg<sup>2+</sup> | Na<sup>+</sup> | К<sup>+</sup> | Cl<sup>-</sup> | HCO<sub>3</sub><sup>-</sup> | Acetate | sample_name |feature | material | collection_date | archive | archive_project | archive_accession
---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---

For the *common_libraries* table

project_name | publication_year | publication_doi | sample_name | archive | archive_project | archive_sample_accession | library_name | strand_type | library_polymerase | library_treatment | library_concentration | PCR_cycle_count | instrument_model | library_layout | library_strategy  | amplicon_variable_region | read_count | archive_data_accession | download_links | download_md5s | download_sizes
---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---

9) Fill in the appropriate columns with the data

![Image alt](/assets/image/instructions/google2.png)

10) Save each sheet of the table in tsv format

![Image alt](/assets/image/instructions/spreadsheet_saving.png)

11) As a result you will have 2 tables
> PRJNA729662 - libraries.tsv

> PRJNA729662 - samples.tsv

12) Table of contents 

![Image alt](/assets/image/instructions/examples.png)

13) Go back to your fork on github. Create a **new branch** and name it in project_name in AuthorYear format

![Image alt](/assets/image/instructions/new_branch.png)

14) Open the tables in the repository and click on `pencil` to modify the table *common_libraries*.

![Image alt](/assets/image/instructions/git1.png)

15) Go to the bottom of the table and enter your data and click the `Commit changes` button

![Image alt](/assets/image/instructions/add_libraries.png)

16) Specify project_name in AuthorYear format in the commit name

![Image alt](/assets/image/instructions/SierraGarcia2020.png)

17) Repeat steps 13-15 for the *common_samples* table

18) Go back to the main page of your repository fork. Note that the branch is not main, but the branch you created for the article you are adding! Click the `Contribute` button to create a pull request and submit your changes to our repository

![Image alt](/assets/image/instructions/open_PR.png)

19) Also specify project_name in AuthorYear format in the name of the created pull request and click the `Create pull request` button

![Image alt](/assets/image/instructions/create_PR.png)

20) This completes the data addition, thank you for your participation!