import csv
import os.path
import re

class Normalizer(object):
    # Maps section name digits to actual alphabetical names of the section
    section_name_mapper = {}
    # Maps section name (alphabetical name along with digit) to section id
    section_name_to_id = {}
    # Maps section id to row id, and each row id is a dict that maps to row name
    section_id_to_row = {}

    def __init__(self):
        pass

    def read_manifest(self, manifest):
        """reads a manifest file

        manifest should be a CSV containing the following columns
            * section_id
            * section_name
            * row_id
            * row_name

        Arguments:
            manifest {[str]} -- /path/to/manifest
        """

        # Sanitize input
        if not os.path.isfile(manifest):
            print "The file does not exist, did not read manifest file"
        elif not manifest.endswith(".csv"):
            print "The file is not in CSV format, did not read manifest file"

        with open(manifest, 'rb') as csvfile:
            # Skip the first line because they are labels for the columns
            next(csvfile)
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in reader:
                # Strip all the leading 0's in any number
                for index in range(len(row)):
                    elem = row[index]
                    if elem is not None:
                        if elem.isdigit() and int(elem) > 0:
                            row[index] = elem.lstrip("0")
                        elif not elem.isdigit():
                            row[index] = elem.lower()
                section_id, orig_section_name, row_id, row_name = row

                self.section_name_to_id[orig_section_name] = section_id

                # For section_name, in order to parse it better, 
                # grab number, and alphabet name
                # Original section_name has letters and a number
                digits_only = re.findall("\d+", orig_section_name)
                if len(digits_only) > 0:
                    digits_only = digits_only[0]
                    section_name = orig_section_name.replace(digits_only, "").strip()
                    if section_name == '':
                        section_name = orig_section_name
                else:
                    # Case where section name has no digits
                    digits_only = section_name.strip()

                # Add numerical part of section name as key, alphabetical
                # part of section name as value to section_name_to_id dict
                if digits_only in self.section_name_mapper:
                    self.section_name_mapper[digits_only].add(section_name)
                else:
                    self.section_name_mapper[digits_only] = {section_name}

                # Add section id as is to section_id_to_row dict, which maps
                # section_id to the row names in that section
                if section_id in self.section_id_to_row:
                    self.section_id_to_row[section_id][row_name] = row_id
                else:
                    self.section_id_to_row[section_id] = {row_name: row_id}

    def compare_letters_with_phrase(self, letters, phrase):
        """Compares letters with phrase to see whether the letters
        are found in the phrase

        It checks whether the letters are found in the correct ordering
        in the phrase. For example, "fd" and "field" will match, since 
        the "f" is found in "field" before the "d" is found. "fd" and 
        "dumbfounded" will not match, since "f" is not found before "d"

        Input:
            letters - a string that may or may not be a real word
            phrase - to be compared to

        Output:
            phrase if the letters are found in it in order; nothing if not
        """

        tmp_phrase = phrase
        while len(letters) > 0:
            found = tmp_phrase.find(letters[0])
            if found > -1:
                tmp_phrase = tmp_phrase[found + 1:]
                letters = letters[1:]
            else:
                return
        return phrase

    def find_closest_word(self, section, set_of_names):
        """Finds given section name in set_of_names

        Input:
            section - section name to be found in set_of_names
            set_of_names - set of names to which the digit in the
                original section name corresponds

        Output:
            string of phrase combined with digit for which is used in
            section_name_to_id lookup
        """

        # Find the word-only section name
        digits_only = re.findall("\d+", section)
        if len(digits_only) > 0:
            digits_only = digits_only[0]
            section = section.replace(digits_only, "").strip()

        # Check whether section name is as is in the set of names
        if section in set_of_names:
            return section + " " + digits_only

        # Iterate through all the phrases in set_of_names
        for phrase_in_name_set in set_of_names:

            # Check whether any words in set of names is in the section name
            # For example, this would catch section name "Preferred Reserve" 
            # and "Reserve" in set_of_names
            if phrase_in_name_set in section:
                return phrase_in_name_set + " " + digits_only

            # Separate the words in each entry in set_of_names
            name_set_words = phrase_in_name_set.split(" ")

            # Iterate through each word in each phrase of set_of_names
            for set_word in name_set_words:

                # Check whether any words in the section name matches any word
                # in the set of names
                # For example, this would catch section name "Field" and 
                # "Field Box" in set_of_names
                if section == set_word:
                    return phrase_in_name_set + " " + digits_only

                # Separate out the words in section
                section_words = section.split(" ")

                # Iterate through each word in section
                for section_word in section_words:

                    # Check whether any one word in section name matches 
                    # any one word in any of the set of names
                    # To do this, compare each word in section and each word of 
                    # each entry in set_of_names
                    # For example, this would catch section name 
                    # "Preferred Field Value" and "Field Box" in set_of_names
                    # They both have the word "Field", so they match
                    if section_word == set_word:
                        return phrase_in_name_set + " " + digits_only
                
                    # Compare each letter in word with the phrase 
                    # from set_of_names
                    result = self.compare_letters_with_phrase(section_word, \
                    phrase_in_name_set)
                    if result is not None:
                        return result + " " + digits_only

        return section

    def normalize(self, section, row):
        """normalize a single (section, row) input

        Given a (Section, Row) input, returns (section_id, row_id, valid)
        where
            section_id = int or None
            row_id = int or None
            valid = True or False

        Arguments:
            section {[type]} -- [description]
            row {[type]} -- [description]
        """
        # Outputs
        section_name = None
        row_id = None
        valid = False

        # Get rid of leading zeroes from the input
        section = section.lstrip("0").lower()
        row = row.lstrip("0").lower()

        # Find the section_number
        section_number = re.findall("\d+", section)
        if len(section_number) > 0:
            section_number = section_number[0].lstrip("0")
        else:
            section_number = None

        # Find the section_name
        if section_number is not None:
            section_name = self.section_name_mapper[section_number]
            if len(section_name) == 1:
                section_name = section_name.pop()
                self.section_name_mapper[section_number].add(section_name)
                if section_name != section_number:
                    section_number = section_name + " " + section_number
            else:
                section_number = self.find_closest_word(section, \
                self.section_name_mapper[section_number])
        
        # Get the section_id
        section_id = self.section_name_to_id.get(section_number)

        # Get the row_id
        if section_id is not None:
            section_id = section_id.lstrip("0")
            row_id = self.section_id_to_row.get(section_id).get(row)
            section_id = int(section_id)
        if row_id is not None:
            row_id = int(row_id)
            valid = True

        return (section_id, row_id, valid)
