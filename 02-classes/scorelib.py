#!/usr/bin/env python3

import re

class Print:
    def __init__(self, edition, print_id, partiture):
        self.edition = edition
        self.print_id = print_id
        self.partiture = partiture

    def format(self):
        print("Print Number:", self.print_id)
        self.composition().format()
        self.edition.format()
        if self.partiture:
            print("Partiture: " + "yes")
        else:
            print("Partiture: " + "no")
        if self.composition().incipit == None:
            print("Incipit:")
        else:
            print("Incipit: " + self.composition().incipit)

    def composition(self):
        return self.edition.composition

class Edition:
    def __init__(self, composition, authors, name):
        self.composition = composition
        self.authors = authors
        self.name = name

    def format(self):
        if self.name:
            print("Edition: " + self.name)
        else:
            print("Edition:")

        print("Editor: ", end="")
        sep = ""
        for author in self.authors:
            print(sep + author.format(), end="")
            sep = ", "
        print()

        for i in range(len(self.composition.voices)):
            print("Voice {}: {}{}".format(i + 1, 
                  self.composition.voices[i].range + ', ' if self.composition.voices[i].range is not None else "", 
                  self.composition.voices[i].name if self.composition.voices[i].name is not None else ""))

class Composition:
    def __init__(self, name, incipit, key, genre, year, voices, authors):
        self.name = name
        self.incipit = incipit
        self.key = key
        self.genre = genre
        self.year = year
        self.voices = voices
        self.authors = authors

    def format(self):
        print("Composer: ", end="")
        sep = ""
        for author in self.authors:
            print(sep + author.format(), end="")
            sep = "; "
        print()

        if self.name:
            print("Title: " + self.name)
        else:
            print("Title:")
        if self.genre:
            print("Genre: " + self.genre)
        else:
            print("Genre:")
        if self.key:
            print("Key: " + self.key)
        else:
            print("Key:")
        if self.year:
            print("Composition Year: " + str(self.year))
        else:
            print("Composition Year:")

class Person:
    def __init__(self, name, born, died):
        self.name = name
        self.born = born
        self.died = died

    def format(self):
        s = self.name
        if self.born:
            years = str(self.born) + "--"
        else:
            years = "--"
        if self.died:
            years += str(self.died)
        if years != "--":
            s += " (" + years + ")"
        return s

class Voice:
    def __init__(self, name, range):
        self.name = name
        self.range = range

def create_person(str_name):
    r_all = re.compile(r"(.*)\((\d{4})-{1,2}(\d{4})\)")
    r_born1 = re.compile(r"(.*)\((\d{4})-{1,2}\)")
    r_born2 = re.compile(r"(.*)\(\*(\d{4})\)")
    r_died1 = re.compile(r"(.*)\(-{1,2}(\d{4})\)")
    r_died2 = re.compile(r"(.*)\(\+(\d{4})\)")

    m = r_all.match(str_name)
    if m:
        name = m.group(1)
        name = name.strip()
        return Person(name, int(m.group(2)), int(m.group(3)))

    m = r_born1.match(str_name)
    if m:
        name = m.group(1)
        name = name.strip()
        return Person(name, int(m.group(2)), None)
        
    m = r_born2.match(str_name)
    if m:
        name = m.group(1)
        name = name.strip()
        return Person(name, int(m.group(2)), None)
        
    m = r_died1.match(str_name)
    if m:
        name = m.group(1)
        name = name.strip()
        return Person(name, None, int(m.group(2)))

    m = r_died2.match(str_name)
    if m:
        name = m.group(1)
        name = name.strip()
        return Person(name, None, int(m.group(2)))

    str_name = str_name.strip()
    return Person(str_name, None, None)

def string_or_none(s):
    result = s.strip()
    if len(result) == 0:
        result = None
    return result

def create_composition(current_print):
    name = None
    incipit = None
    genre = None
    key = None
    year = None
    authors = []
    voices = []
    for line in current_print:
        if "Title:" in line:
            line = line.replace("Title:", "")
            name = string_or_none(line)
        elif "Incipit:" in line:
            line = line.replace("Incipit:", "")
            incipit = string_or_none(line)
        elif "Key:" in line:
            line = line.replace("Key:", "")
            key = string_or_none(line)
        elif "Genre:" in line:
            line = line.replace("Genre:", "")
            genre = string_or_none(line)
        elif "Composition Year:" in line:
            line = line.replace("Composition Year:", "")
            line = line.strip()
            r = re.compile(r"(.*)(\d{4})(.*)")
            m = r.match(line)
            if m:
                year = int(m.group(2))
            else:
                year = None
        elif "Composer:" in line:
            line = line.replace("Composer:", "")
            composer_list = line.split(";")
            for name in composer_list:
                name = name.strip()
                authors.append(create_person(name))
        else:
            r = re.compile(r".*Voice \d:(.*)")
            line = line.strip()
            m = r.match(line)
            if m:
                s = m.group(1)
                s = s.strip()
                r_range = re.compile(r"(\w*)--(\w*)")
                m_range = r_range.match(s)
                if m_range:
                    voice_range = m_range.group(1) + "--" + m_range.group(2)
                    voice_name = s.replace(voice_range, "")
                    voice_name = voice_name.strip()
                    if len(voice_name) > 0 and voice_name[0] == ",":
                        voice_name = voice_name[1:]
                    if len(voice_name) > 0 and voice_name[0] == " ":
                        voice_name = voice_name[1:]
                    voice_name = voice_name.strip()
                    if len(voice_name) > 0:
                        voices.append(Voice(voice_name, voice_range))
                    else:
                        voices.append(Voice(None, voice_range))
                elif len(s) > 0: # not range
                    voice_name = s
                    voices.append(Voice(voice_name, None))
                else:
                    voices.append(Voice(None, None))
    return Composition(name, incipit, key, genre, year, voices, authors)

def create_edition(current_print):
    name = None
    authors = []
    for line in current_print:
        if "Edition:" in line:
            line = line.replace("Edition:", "")
            name = line.strip()
            if len(name) == 0:
                name = None
        elif "Editor:" in line:
            line = line.replace("Editor:", "")
            editor_names = line.split(",")

            r = re.compile(r"(.*)\s(.*)")
            first_name = None
            for editor_name in editor_names:
                editor_name = editor_name.strip()
                if r.match(editor_name) and first_name == None:
                    authors.append(Person(editor_name, None, None))
                elif r.match(editor_name): #first_name needs to be processed
                    authors.append(Person(first_name, None, None))
                    first_name = None
                    authors.append(Person(editor_name, None, None))
                elif first_name == None: # set new first name
                    first_name = editor_name
                else: # combine first name and current editor_name as one
                    combined_name = first_name + " " + editor_name
                    authors.append(Person(combined_name, None, None))
                    first_name = None
            if first_name != None: # process last name
                authors.append(Person(first_name, None, None))
    return Edition(create_composition(current_print), authors, name)

def create_print(current_print):
    print_id = 0 
    partiture = False
    for line in current_print:
        if "Print Number:" in line:
            line = line.replace("Print Number:", "")
            line = line.strip()
            print_id = int(line)
        elif "Partiture:" in line:
            partiture = ("yes" in line)
    return Print(create_edition(current_print), print_id, partiture)

def load(file_name):
    file = open(file_name, 'r')
    print_list = []
    current_print = []
    for line in file:
        line = line.strip()
        if line == "" and len(current_print) == 0: # skip lines before Print
            continue
        elif line == "": # and current_print != 0 -> Print is complete
            print_list.append(create_print(current_print))
            current_print.clear()
        else: # add one line of Print
            current_print.append(line)
    if len(current_print) != 0: # create last Print
        print_list.append(create_print(current_print))

    file.close()
    return print_list
