# README 

BioVal is a validation tool for crossvalidation of an imput file to upload on RedCAP and a ref file (the already existing data on RedCAP). 
The code runs locally and is fully python based and prevents the loss of information as the RedCap Importfile system is not reliable enough to perform
the validation tasks. 

## Dependencies
 - csv (inbuild python 3.9) 
 - tkinter (8.6.11 Conda)
 - sys (3.9.12 Conda) 
 - regex (2022.3.15 Conda)
 - Pillow (9.0.1 - PIP)

## How to use BioVal? 

The package can be either used as jupyter notebook directly or as Graphical Interface. In both cases this is what you need: 

- csv input file in BioVal/templates/
- csv ref file at the moment as direct download from redcap
- csv lab ID file (this is not setup, but you wanted to use the patIDs instead of TreatHSP locally, this file needs to be stored, backed up and filled everytime you do an upload!)

The inbuild functions of the BioVal Package first validate the input and ref files row by row in the csv file, such that it will detect any errors for example in the input file AND in the ref file! This sound
paranoid, but in case somebody unintantionally makes a mistake while entring data manually on the RedCap repository, it is necessary to double check the ref file. Easiest way, would be to also 
give the write function on the Biorepository in RedCap only to people which should have it. But just in case, the functionality of BioVal tackels both sides of the input and ref files to avoid any
mistakes. 

The main task of the BioVal functions is to ensure the input is correct for any chosen Biofluid (Serum, EDTA Plasma, Urin, CFR, CFR pellets)  or culture (Fibroblasts, PAXgene, PBMC, DNA), e.g. the Biofluids must be stored
in the -80°C freezers and not in the nitrogen freezer ([-150,-196]°C). Also the structure of the box, rack system is in both cases slidly different such that the package handels the input. The Biofluids can be stored in racks with in total 6 boxes each; where the boxes cover a matrix of A1-H12 (8x12=96 Kryotubesspaces), whereas the nitrogen .................??? 

In the validation progress also the input is evaluated in case of required fields. It is not possible to upload data without specifying the position or the material type and patient ID. 

After the validation ran BioVal gives a feedback with a small txt file showing all errors that might have occured and giving based on it a recommendation for upload or not upload. 

#### Workflow 

1. Fill in the required variables in the template file (colorcoded)
2. Download the ref file from RedCap repository (here create build in solution)
3. Run validation either with GUI or python
4. Evaluation of the error file
5. In case of positive evaluation, upload on RedCap. In case of negative evaluation BioVal will pinpoint on the specific row in the csv files where problems have occured, such that they should be easy to fix





























--- 

For further information please contact: Aaronjeremia.maas@gmail.com
