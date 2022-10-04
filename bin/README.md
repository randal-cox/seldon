# Commands for Project Seldon

# meta commands
- coverage - display coverage of tests; add --runslow to handle slow spark commands
- test - run all tests ; add --runslow to handle slow spark commands
- setup - install all required modules
- source - source this file before working with seldon
- jupyter - launch the jupyter server
- docker - launch docker in a new bash shell

# main commands
- demo - a short script to demo the logger and spark
- tree - a tree building program
- action - use a tree and some records to chart minimal action to change outcomes
- rules - convert a tree to optimal rules describing nodes with the best FPR

# training data
All training data used by tree should meet the following criteria for fields. 
Text-based input files must be tab-separated and lines should be newline sepearated.
Parquet files should have a ll fields typed appropriately.

## Input Fields
Input fields should be named starting with a capital letter to distinguish from 
the meta fields when the data file is a text file. 

## Meta Fields
- outcome - the outcome, usually 0 or 1
- weight - the number of records this row represents, defaults to 1
- volume - the intensity of the record (e.g., the population)
- entity - the entity this row is associated with (e.g., the country)
- time - the time index of the record (in datetime, date, or time)
- marked - if this row was already marked by other methods besides this model (0 or 1)
- set - 0 if training, 1 if holdout, 2 if out-of-time
- 