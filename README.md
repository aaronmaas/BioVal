# README 

BioVal is a validation tool for crossvalidation of an imput file (import file) to upload on RedCAP and a ref file (the already existing data on RedCAP). 
The code runs locally and is fully python based and prevents the loss of information as the RedCap data import system is not reliable enough to perform the validation tasks. 

## Dependencies
 - csv (inbuild python 3.9)
 - os (inbuild python 3.9)
 - subprocess (inbuild python 3.9)
 - collections (inbuild python 3.9)
 - re (inbuild python 3.9)
 - tkinter (8.6.11 Conda)
 - sys (3.9.12 Conda) 
 - regex (2022.3.15 Conda)
 - Pillow (9.0.1 - PIP)
 - pyinstaller (6.18.0 - PIP)

## How to use BioVal? 

The package can used via a graphical interface. 

#### Quickstart:

In your Terminal with conda environment:
- type python BioVal.py 
- follow the instructions

 Here is what you need to start:
- csv template file in BioVal/templates/
- csv ref file at the moment as direct download from redcap
- csv data to upload from scan 

The inbuild functions of the BioVal Package first validate the input and ref files row by row in the csv file, such that it will detect any errors for example in the input file AND in the ref file! This sound
paranoid, but in case somebody unintantionally makes a mistake while entring data manually on the RedCap repository, it is necessary to double check the ref file. 

#### Functionalities

The main task of the BioVal functions is to ensure the input is correct for any chosen Biofluid (Serum, EDTA Plasma, Urin, CFR, CFR pellets)  or culture (Fibroblasts, PAXgene, PBMC, DNA), e.g. the Biofluids must be stored
in the -80°C freezers and not in the nitrogen freezer ([-150,-196]°C). Also the structure of the box, rack system is different for e.g. Biofluids and PAXgene. For the values that are allowed to be entered please refer to BioVal/templates/RDRegistry_Import_variable_values.xlsm . There you find an overview about the required fields and there respective values.

After the validation ran BioVal gives a feedback with a small txt file showing all errors that have occured. It is to be reviewed carefully!

#### Workflow BioVal validated Upload the RedCap

1. Open BioVal  
    - Either run python BioVal.py in /BioVal directory
    - or run application in /BioVal/dist 
2. Click Button Start BioVal
3. Select Biomaterial which should be integrated; 
    - for every Biomaterial you want to include you would need to actually make one BioVal round
4. BioVal generates the avaialble positions for the Biomaterial 
    - save where you would like the available positions csv (you can copy from here directly positions) be careful to not change the name so that it gets overwritten and you dont exidently use an old one!
    - BioVal opens the new csv - depending on the material 
    - BIOFLUIDS in One box at least 15 spots must be free (maximum number of free positions shown 40)
    - PAXGene, DNA  also single positions are shown (15 free positions are shown) 
5. Cut positions out in the template file and safe it as import file 
    - don't copy, I think it is safer that way; but the validation should also take care of it otherwise
6. Select the generated import file
7. Validate (BioVal handles it)
    - import file
    - reference file
8. Save report
9. Inspect report
    - if hard errors occur, things that cannot be tolerated; the programm terminates with the explicit ValueError or ValidationError. In the row by row validation the errors are stored to the save report. In case of a hard error, the programm terminates without generating a report but showing the error! 
    - review carefully!
10. Go To RedCap to DATA import tool and import the validated import file. 
11. Review the changes shown by RedCap. Import file.
11. Delete the import file. 

#### BioVal validated status change: 



#### How to install: 

1. Get anaconda
    - https://www.anaconda.com/docs/getting-started/anaconda/install/overview 
    - choose then your operational system and graphical download
    - follow the instructions
2. Get git
    - https://github.com/git-guides/install-git 
    - for MacOs it can be necessary to use
        - xcode-select --install  command in the terminal!
3. Install BioVal 
   - write in terminal at the location you want to install BioVal (e.g. Desktop) 
       - git clone https://github.com/aaronmaas/BioVal.git
4. Optional: Build completly clickable version
   - 
































--- 

For further information please contact: Aaronjeremia.maas@gmail.com
