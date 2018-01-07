# Aggie Bookstore Lookup

This project automates the process of looking up required books for courses.

### Installation and Use

1. Install the packages required to run this program with "pip install -r requirements.txt"
2. Create the file NAME.csv with the current course information for the person named NAME in the directory "include" (see below for formatting)
3. Update term.txt with what semester is being processed: F for fall, S for spring followed by 2-digit year (e.g. F17, S18)
4. Run "python main.py"
5. Read the results from books.csv

### Input Data Format
An example of the data format can be found in "include/Jon Janzen.csv.template"

A header line with the content "DEPARTMENT,NUMBER,SECTION" is optional and may be included for readability.

The format is basically:

1. 4-character department code (e.g. CSCE)
2. 3-digit course number (e.g. 121)
3. 3-digit section number (e.g. 501)

It is common for different professors to assign different text books so section is required.
