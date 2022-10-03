# Input Fields
Input fields should be named starting with a capital letter to distinguish from 
the meta fields. 

Fields should be typed in the parquet file

# Meta Fields
- outcome - the outcome, usually 0 or 1
- weight - the number of records this row represents, defaults to 1
- volume - the intensity of the record (e.g., the population)
- entity - the entity this row is associated with (e.g., the country)
- time - the time index of the record (in datetime, date, or time)
- marked - if this row was already marked by other methods besides this model (0 or 1)
- set - 0 if training, 1 if holdout, 2 if out-of-time


