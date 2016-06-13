# Code Design for Section Normalization
## Reading Manifest file
The input manifest file gets read in read_manifest(self, manifest). This function parses the file row by row, separating out the different columns per each row. In the row data, we have section name, section id, row name, and row id. It parses this data then stores it into three dictionaries (for which all keys are strings):
- section_name_mapper: this maps the digit part of the section name to all the word-parts of the section name. For example, if "Box Level 6" and "Top Deck 6" are both section names, this dictionary will have key "6" with value ["Box Level", "Top Deck"]. If the section name is only "104", then key "104" will have value ["104"]. If the section name doesn't include a number and is words only, the key and value will both the original section name.
- section_name_to_id: this maps the entire section name to its corresponding id. For example, if "Box Level 6" has section id "10", this dictionary will have key "Box Level 6" with value "10".
- section_id_to_row: this maps the section id to another dictionary. Every value of section_id_to_row is another dictionary, in which the key is the row name and the value is the row id. For example, if section 216 has a row with name 'a', and this row name has row id '1', section_id_to_row will have key "216" with value {'a':'1'}.

## Normalizing an Input
Given the section name and row name, the application needs to output a section_id, row_id, and whether this is found in the manifest file.

### Finding the section ID
Many steps are tried to see whether there's a matching section ID.<br>
1. Section name gets parsed into digits and words.<br>
2. The digit gets looked up in section_name_mapper, and the set of corresponding words get passed back. <br>
    a. If the digit itself is found in the list, the application will use this to look in section_name_to_id to get that section name's ID. This takes care of the case for when the section name is digit-only as well. 
    b. If the digit itself is not found, the application will use the word-only part of the section name to try to make matches in the set of words. To do this, it will see whether the name is in the set, whether part of the name matches any items in the set, whether any items in the set matches any words in the name, and whether the letters in the name are found in the same order as any set items.
    c. After it gets the matching word or phrase from the set, the application uses the word/phrase attached with the digit part ef the original section name to get the corresponding section id from the section_name_to_id dictionary.
3. If there is no matching section id from the given section name, the program will return "False" for validity of input.

### Finding the row ID
Assuming the section id is found from the given section name, the section id is used to get all the row names, which will in turn eturn the right row id. 
1. If the section id exists in the section_id_to_row dictionary, it will return a dictionary mapping row names to keys for that particular section. 
2. Using the given row name in the input, the program will look in this dictionary whether the row name exists, and if it does, return the corresponding row id.
