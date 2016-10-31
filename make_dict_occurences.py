'''
Created on 20.05.2015

@author: Thomas Graichen (www.tgraichen.de)

'''

import csv


def dict_pointID_countOccurences(csv_file):

   result_dict = {}
   itemlistInput_path = csv_file

   itemlist_file = open(itemlistInput_path, 'r')
   itemlist_csv = csv.reader(itemlist_file, delimiter=',')
   next(itemlist_csv)                                 #skip first line (header)


   for index, row in enumerate(itemlist_csv):             #loop through rows in our csv-file
      counter = 0
      for i, item in enumerate(row):
         if item == "TRUE":
            counter += 1
      result_dict[row[0]] = counter

   itemlist_file.close()
   return result_dict

mydict = dict_pointID_countOccurences("all_settlements.csv")

outfile = open( 'dict_test.csv', 'w' )
for key, value in sorted( mydict.items() ):
    outfile.write( str(key) + ',' + str(value) + '\n' )
outfile.close()
