#!/usr/bin/env python
#
# iwlistparse.py
# Hugo Chargois - 17 jan. 2010 - v.0.1
# Parses the output of iwlist scan into a table

# Taken from here: https://bbs.archlinux.org/viewtopic.php?id=88967

import sys
import re

# You can add or change the functions to parse the properties of each AP (cell)
# below. They take one argument, the bunch of text describing one cell in iwlist
# scan and return a property of that cell.

def get_name(cell):
    return '"' + matching_line(cell,"ESSID:")[1:-1] + '"'

def get_quality(cell):
    quality = matching_line(cell,"Quality=").split()[0].split('/')
    return str(int(round(float(quality[0]) / float(quality[1]) * 100))).rjust(3)

def get_signal(cell):
    quality = matching_line(cell,"Quality=").split()[2].split('=')
    return str(quality[1]).rjust(3)

def get_noise(cell):
    quality = matching_line(cell,"Quality=").split()[5].split('=')
    return str(quality[1]).rjust(3)

def get_channel(cell):
    l = matching_line(cell,"Channel:")
    if l is not None:
        return l
    l = matching_line(cell,"Frequency:")
    return re.match('(.*) GHz \(Channel (.*)\)', l).group(2)

def get_encryption(cell):
    enc=""
    if matching_line(cell,"Encryption key:") == "off":
        enc="Open"
    else:
        for line in cell:
            matching = match(line,"IE:")
            if matching!=None:
                wpa=match(matching,"WPA Version ")
                if wpa!=None:
                    enc='"' + "WPA v."+wpa + '"'
                wpa=match(matching,"IEEE 802.11i/WPA2 Version ")
                if wpa!=None:
                    enc='"' + "WPA2 v."+wpa + '"'
        if enc=="":
            enc="WEP"
    return enc

def get_address(cell):
    return matching_line(cell,"Address: ")

# Here's a dictionary of rules that will be applied to the description of each
# cell. The key will be the name of the column in the table. The value is a
# function defined above.

rules={"Name":get_name,
       "Quality":get_quality,
       "Signal":get_signal,
       "Noise":get_noise,
       "Channel":get_channel,
       "Encryption":get_encryption,
       "Address":get_address,
       }

# Here you can choose the way of sorting the table. sortby should be a key of
# the dictionary rules.

def sort_cells(cells):
    sortby = "Quality"
    reverse = True
    cells.sort(None, lambda el:el[sortby], reverse)

# You can choose which columns to display here, and most importantly in what order. Of
# course, they must exist as keys in the dict rules.

columns=["Name","Address","Quality","Signal","Noise","Channel","Encryption"]




# Below here goes the boring stuff. You shouldn't have to edit anything below
# this point

def matching_line(lines, keyword):
    """Returns the first matching line in a list of lines. See match()"""
    for line in lines:
        matching=match(line,keyword)
        if matching!=None:
            return matching
    return None

def match(line,keyword):
    """If the first part of line (modulo blanks) matches keyword,
    returns the end of that line. Otherwise returns None"""
    line=line.lstrip()
    length=len(keyword)
    if line[:length] == keyword:
        return line[length:]
    else:
        return None

def parse_cell(cell):
    """Applies the rules to the bunch of text describing a cell and returns the
    corresponding dictionary"""
    parsed_cell={}
    for key in rules:
        rule=rules[key]
        parsed_cell.update({key:rule(cell)})
    return parsed_cell

def print_table(table):
    widths=map(max,map(lambda l:map(len,l),zip(*table))) #functional magic

    justified_table = []
    for line in table:
        justified_line=[]
        for i,el in enumerate(line):
            justified_line.append(el.ljust(widths[i]+2))
        justified_table.append(justified_line)
    
    for line in justified_table:
        for el in line:
            print el,
        print

def print_cells(cells):
    table=[columns]
    for cell in cells:
        cell_properties=[]
        for column in columns:
            cell_properties.append(cell[column])
        table.append(cell_properties)
    print_table(table)

def mainFile():
    """Pretty prints the output of iwlist scan into a table"""
    cells=[[]]
    parsed_cells=[]

    for line in sys.stdin:
        cell_line = match(line,"Cell ")
        if cell_line != None:
            cell_zero = match(cell_line,"01 - ")
            if cell_zero != None:
                cells=[[]]
            cells.append([])
            line = cell_line[-27:]
        cells[-1].append(line.rstrip())

    cells=cells[1:]

    for cell in cells:
        parsed_cells.append(parse_cell(cell))

    sort_cells(parsed_cells)

    print_cells(parsed_cells)

def print_line(cell):
    widths=[20, 20, 4, 4, 4, 4, 10]
    for i,el in enumerate(columns):
        sys.stdout.write(cell[el].ljust(widths[i]+2))
    sys.stdout.write('\n')
    sys.stdout.flush()

def mainStream():
    cell = None
    """Pretty prints the output of iwlist scan into a table"""
    for line in sys.stdin:
        cell_line = match(line,"Cell ")
        if cell_line != None:
            if cell != None:
                print_line(parse_cell(cell))
            cell = []
            line = re.match('Cell ([0-9]*) - (Address: .*)', line.strip()).group(2)
        if cell is not None:            
            cell.append(line.rstrip())

mainStream()
#mainFile()
