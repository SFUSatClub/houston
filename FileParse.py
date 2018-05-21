""" File handler
    - this module handles dealing with files downloaded from the OBC including:
        - reconstructing files 
        - formatting file file commands so we don't need to think in ASCII
"""

from houston_utils import string_find as string_find
import datetime
import csv
import os
name_from_suffix = {'A': 'FSYS_SYS', 'B':'FSYS_ERROR', 'C': 'OBC_CURRENT'}
suffix_from_name =  dict(zip(name_from_suffix.values(),name_from_suffix.keys()))

class FileParse():
    def __init__(self):
        self.file_download = False
        self.prefix = 'a'
        self.suffix = 'A'
        self.reported_size = 0
        self.file_raw_data = ''

    def process_raw(self, line):
        """ Determines if data from OBC is file-related, 
        starts writing it if yes. Creates/closes local log files"""
        self.line = line

        if not self.file_download:
            if string_find(line, 'FILE: '):
                print ('Captured file')
                self.file_download = True
                self.update_meta()
                self.create_file()
            else:
                pass
        else:   # we're actively capturing a file
            """ Methodology: read the file contents into a string, then break the string up and write to .csv """
            if string_find(line, 'FILE_END: '):
                print('finishing file write')

                self.file_download = False
                self.csvwriter.writerow(['Epoch','Data'])
                data_line = self.file_raw_data.split('\7')
                """ Remove newlines and split, results in properly concatenated data """
                for item in data_line:
                    item = item.replace('\r','')
                    item = item.replace('\n','')
                    item = item.split('|')
                    if len(item) > 1:
                        self.csvwriter.writerow(item)

                self.csvfile.close()
                self.file_raw_data = ''
            else:
                self.file_raw_data = self.file_raw_data + str(self.line)


    def update_meta(self):
        """ Update the metadata from the first file read telem from OBC """
        # note: must account for the OBC returning 'aA' as an ack for the command (it comes in through the line too)        
        self.prefix = self.line[8]
        self.suffix = self.line[9]
        self.reported_size = int(self.line [11:])

    def create_file(self):
        """Creates the log file we download into, writes out the header"""

        path = 'sat_download_files/' + str(datetime.datetime.now().strftime("%Y-%m-%d")) + '/'
        print(path)
        if not os.path.exists(path):
            os.makedirs(path)
        
        file_fullpath = path + '/' + self.prefix + self.suffix + '-' + datetime.datetime.now().strftime("%H:%M") + '.csv'
        
        self.csvfile =  open(file_fullpath, 'w', newline='')
        self.csvwriter = csv.writer(self.csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)

        # add the data log header
        self.csvwriter.writerow(['Prefix', 'Suffix', 'Log Name', 'Download Time', 'Reported Size'])
        self.csvwriter.writerow([self.prefix, self.suffix, name_from_suffix[self.suffix],datetime.datetime.now(), self.reported_size])
        return


def create_dump_command(input_cmd):
    """ Since the OBC takes hex-encoded arguments for the file suffix and prefix, 
    this function is an easy way to create a dump command that the OBC can understand"""

    toks = input_cmd.split(" ")
    if len(toks[2]) == 2:   # "file dump aA" - we have the raw aA style of file name
        # file dump prefixsuffix
        if not str(toks[2]).isnumeric():
            fname = toks[2]
            pre = str(format(ord(fname[0]), 'x')) # letter to ascii decimal code, then hex
            suf = str(format(ord(fname[1]), 'x'))
        else:
            pre = str(toks[2])[0:1]
            suf = str(toks[2])[2:]

    elif len(toks) == 4:
        if len(toks[-1]) == 1:  # file fump a A
            pre = str(format(ord(toks[2]), 'x'))
            suf = str(format(ord(toks[3]), 'x'))
        else:                   # file dump a FSYS_SYS
            pre = str(format(ord(toks[2]), 'x'))
            suf = str(format(ord(suffix_from_name[toks[3]]), 'x'))
 
    return toks[0] + ' ' + toks[1] + ' '+ pre + suf
