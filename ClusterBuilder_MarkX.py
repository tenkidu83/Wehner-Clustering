'''
Created on 20.05.2015

@author: Thomas Graichen (www.tgraichen.de)

'''

import csv
import math
import os
import collections

class ClusterBuilder(object):
  """takes csv and creates clusters"""

  def __init__(self, csv_file, distance_levels):
    self.csv_file = csv_file
    self.distance_levels = int(distance_levels)

    self.radii_list = None
    self.list_dicts_clusters_using_radii = None
    self.dict_distancelevels_perID = None
    self.dict_median_of_distancelevels_perID = {}
    self.dict_num_connections_across_DL = None
    self.g_dict_networkCentrality_ID = None

    print("init new ClusterBuilder object")
  
  def g_list_radii(self):
    """
    Create a new list (distances_list) of all distances from the distance matrix (self.csv_file).
    Takes the user's distance_levels and the Min/Max distances from the distances_list to create 
    a new list of radii (radii_list) to later iterate through.
    output:
    radii_list =
    [
      radius1, radius2, radius3,...
    ]
    """
    distances_list = []
    radii_list = []
    itemlistInput_path = self.csv_file
    with open(itemlistInput_path, 'r') as itemlist_file:
      itemlist_csv = csv.reader(itemlist_file, delimiter=',')
      next(itemlist_csv)
      for i, row in enumerate(itemlist_csv):           
        distance = float(row[2])
        distances_list.append(distance)            
    max_dist = max(distances_list)
    min_dist = min(distances_list)
    range_dist = max_dist - min_dist
    radius_step = range_dist / (self.distance_levels)
    radius = min_dist + radius_step
    while radius <= max_dist:
      radii_list.append(radius)
      radius += radius_step

    self.radii_list = radii_list
    
    return radii_list

  def dict_from_distancematrix_using_radius(self, radius, FILTERDICT = {}):
    """
    Using a distance matrix, create a dictionary with pointIDs as keys and a list of targetIDs as value, ignoring connections above radius.
    If a FILTERDICT (created by dict_centers_of_clusters()) is present, regard only the pointIDs in FILTERDICT, else regard all of them.
      structure:
      result_dict =
        {
          pointID : [targetID, targetID,...],
          pointID : [targetID, targetID,...],
          ...
        }
    """
    result_dict = {}
    itemlistInput_path = self.csv_file

    l_filterdict_values = FILTERDICT.values()

    itemlist_file = open(itemlistInput_path, 'r')
    itemlist_csv = csv.reader(itemlist_file, delimiter=',')
    next(itemlist_csv)                                 #skip first line (header)
    

    for i, row in enumerate(itemlist_csv):             #loop through rows in our csv-file
      inputID = row[0]                               #make nice references to cells
      targetID = row[1]
      distance = float(row[2])

      if distance <= radius:                          #if the distance is inside our radius:
        if inputID not in result_dict:                 #check if inputID already exists in our dictionary...
           result_dict[inputID] = []                     #...if not so, add a key (inputID) and an empty list                         
        targetID_list = result_dict[inputID]           #reference to nested list result_dict
        targetID_list.append(targetID)                 #put targetID in targetID_list
      else:                                           # ADDED  -  points with connections above radius have to be added also, as keys with an empty list as value
        if inputID not in result_dict:
          result_dict[inputID] = []

    
    result_dict_2 = {}
    if len(l_filterdict_values) > 0:                # if we have a filter...
      for key in result_dict.keys():
        for item in l_filterdict_values:
          if key == item:
            result_dict_2[key] = result_dict[key]
    else:
      for key in result_dict.keys():
        result_dict_2[key] = result_dict[key]

    
    
    result_dict_3 = result_dict_2
    if len(l_filterdict_values) > 0:
      for key, value in result_dict_2.items():
        for pointID in value:
          index = value.index(pointID)
          if pointID not in result_dict_2.keys():
            del result_dict_2[key][index]
      for key, value in result_dict_2.items():                  #second run, necessary, but reason unclear
        for pointID in value:
          index = value.index(pointID)
          if pointID not in result_dict_2.keys():
            del result_dict_2[key][index]
    


   

    itemlist_file.close()
    return result_dict_2

  def dict_clusters_and_their_points(self, INPUTDICT):
    """
    This function takes the output of dict_from_distancematrix_using_radius() -> INPUTDICT and iterates through 
    its targetlists' items and compares them to the following targetlists.
    If a match is found, it converts the two respective lists to sets, makes a union and converts it back to a list.
    The 2nd list is overwriten, and the 1st list is marked in an external list as "to be deleted", and is not taken 
    into consideration in further iterations.
    since we only need one match per list pair, the loop through the second list as well as the loop through the 
    first list's items is broken.
    Then, the entries marked for deletion in oblivion_list are deleted from targetlists_dict.
    Finally, the targetlists are transfered to a dict with consecutive numbers (final_result) for readability's sake.

    structure of final_result:
    {
      clusterID : [pointID, pointID,...],
      ...
    }
    
    """
    targetlists_dict = {}
    
    
    counter = 0
    loopbreaker = 0
    oblivion_list = []

    """take targetlists in INPUTDICT. 
    append these targetlists to targetlists_dict using a consecutive number as key.
    the keys corresponding to the targetlists are appended to the respective lists.
    """
    for item in sorted(INPUTDICT):
      targetlists_dict[counter] = INPUTDICT[item]
      targetlists_dict[counter].append(item)
      counter += 1

    """check for equal numbers in lists"""
    for key in targetlists_dict:                          
      for target in set(targetlists_dict[key]):                 
        for key2 in targetlists_dict:                              
          if (key != key2) and (key2 not in oblivion_list):                                            
            if target in targetlists_dict[key2]:                       
              set1 = set(targetlists_dict[key])                          
              set2 = set(targetlists_dict[key2])
              set_union = set1.union(set2)                               
              union_list = list(set_union)                               
              targetlists_dict[key2] = union_list                        
              oblivion_list.append(key)                                 
              loopbreaker = 1
              break                                                      

        if loopbreaker == 1:                                             
          loopbreaker = 0
          break

    for item in oblivion_list:                                          
      del targetlists_dict[item]


    """now that we have our complete clusters, we make a dict (final_result), containing a list of all targets, with the new consecutive cluster_ID as key"""

    final_result = {}                                                  
    cluster_ID_counter = 0                                              

    for target in targetlists_dict:
      thegoods = targetlists_dict[target]
      final_result[cluster_ID_counter] = thegoods
      cluster_ID_counter += 1

    
    return final_result

  def dict_centers_of_clusters(self, CONNECTIONS_DICT, CLUSTERS_DICT):
    """
    Take the output of 'dict_from_distancematrix_using_radius()'-> CONNECTIONS_DICT 
    and the output of 'dict_clusters_and_their_points()'-> CLUSTERS_DICT for the former.
    make a new dict (clusters_centers)
    For each cluster in CLUSTERS:
      For each point in cluster:
        check it`s attached targetlist in CONNECTIONS_DICT.
        Save the pointID and the length(int) of the targetlist as key/value in a temporary dict.
      Sort our temporary dict by value from highest to lowest, take the first key/value pair...
      ...add clusterID : pointID(center) to clusters_centers
      -> if there is no definitive center, the point is chosen randomly

    these centerpoints are going to be used as a filter(FILTERDICT) in the next iteration of 'dict_from_distancematrix_using_radius()'
    (see 'g_list_dicts_of_clusters_using_radii()' below)

    """

    tempdict = {}
    dict_clusters_centers = {}
    for cluster in CLUSTERS_DICT:
      for point in CLUSTERS_DICT[cluster]:
        try:
          connections = CONNECTIONS_DICT[point]
          lenghtoftargetlist = len(connections)
        except:
          lenghtoftargetlist = 0
        tempdict[point] = lenghtoftargetlist
      sorted_keys_of_tempdict_desc = sorted(tempdict, key=tempdict.get, reverse = True)
      centerpoint = sorted_keys_of_tempdict_desc[0]
      dict_clusters_centers[cluster] = centerpoint
      tempdict = {}

    return dict_clusters_centers

  def g_list_dicts_of_clusters_using_radii(self):

    global_list_of_dicts = []
    radii_list = self.radii_list
    dict_clusterCenters = {}                            
  
    
    for radius in radii_list:                                                                               
      dict_filteredDistMatrix = self.dict_from_distancematrix_using_radius(radius, dict_clusterCenters)            
      dict_clusters = self.dict_clusters_and_their_points(dict_filteredDistMatrix)                                 
      global_list_of_dicts.append(dict_clusters)                                                              
      dict_clusterCenters = self.dict_centers_of_clusters(dict_filteredDistMatrix, dict_clusters)                  


    self.list_dicts_clusters_using_radii = global_list_of_dicts                                             
    return global_list_of_dicts

  def g_dict_number_of_distancelevels_perID(self):
    """
    for each radius in dict produced by dict_from_distancematrix_using_radius():

    Take the dicts in self.list_dicts_clusters_using_radii and look at their values. 
    Make a tempdict {pointID : weight}. 
    If a Point is present as a value, increment its "weight" counter by one for each dict it is found in.
    save result globaly:
      {
        pointID : weight,
        ......
      }
    ...= 'ANZAHL DER DISTANZEBENEN'
    """
    radii_list = self.radii_list
    result_dict = {}
    templist = []
    dict_clusterCenters = {}

    for radius in radii_list:                                                                               
      dict_filteredDistMatrix = self.dict_from_distancematrix_using_radius(radius, dict_clusterCenters)            
      templist.append(dict_filteredDistMatrix)
      dict_clusters = self.dict_clusters_and_their_points(dict_filteredDistMatrix)                                 
      dict_clusterCenters = self.dict_centers_of_clusters(dict_filteredDistMatrix, dict_clusters)                  

    for dictionary in templist:
      for key, value in dictionary.items():
        if len(value) > 1:
          if key not in result_dict.keys():
            result_dict[key] = 1
          else:
            result_dict[key] += 1

    self.dict_distancelevels_perID = result_dict
    return result_dict

  def g_dict_median_of_distancelevels_perID(self):
      """
      = MITTELWERT DER DISTANZEBENEN
      saved as dict:
      {
        pointID : median,
        ...
      }
      """

      radii_list = self.radii_list
      thisdict = self.g_dict_number_of_distancelevels_perID()
      newdict = {}
      for key, value in thisdict.items():
        median = float(value+1)/2
        newdict[key] = median


      self.dict_median_of_distancelevels_perID = newdict
      return newdict

      """
      for item in sorted(newdict):
        print("{}:{}".format(item, newdict[item]))
      print("keys: {}".format(len(newdict.keys())))
      """    

  def g_sum_of_connections_across_distancelevels(self):
      
    """
    Gesamtzahl der Verbindungen:
    Get targetlists' (value) length in all dicts in self.list_dicts_clusters_using_radii for each point (key), get sum and put in new dict (global). 
    
    """
    radii_list = self.radii_list
    result_dict = {}
    templist = []
    dict_clusterCenters = {}

    """fill templist"""
    for radius in radii_list:                                                                               
      dict_filteredDistMatrix = self.dict_from_distancematrix_using_radius(radius, dict_clusterCenters)            
      templist.append(dict_filteredDistMatrix)
      dict_clusters = self.dict_clusters_and_their_points(dict_filteredDistMatrix)                                 
      dict_clusterCenters = self.dict_centers_of_clusters(dict_filteredDistMatrix, dict_clusters)                  
    """fill result_dict"""
    for dictionary in templist:
      for key, value in dictionary.items():
        if key not in result_dict.keys():
            result_dict[key] = len(value) - 1
        else:
          result_dict[key] += len(value) - 1

    self.dict_num_connections_across_DL = result_dict
    return result_dict

  def g_dict_networkCentrality_perID(self):

   
    dict1 = self.g_sum_of_connections_across_distancelevels()
    dict2 = self.g_dict_number_of_distancelevels_perID()
    dict3 = self.g_dict_median_of_distancelevels_perID()

    dict_result = {}

    for key, value in dict1.items():
      dict_result[key] = dict1[key] + dict2[key] + dict3[key]

    self.g_dict_networkCentrality_ID = dict_result
    return dict_result

  def write_outputs_to_file(self):

    """self.radii_list"""
    output_file_path =  str(self.csv_file).replace(".csv", "") + "__inputDL" + str(self.distance_levels) + "_01" + "___list_radii" + ".txt"
    output_file = open(output_file_path, "w")
    output_file.write("#radii calculated by g_list_radii()")    
    #--write rows
    for item in self.radii_list:
      output_file.write("\n{}".format(item))
    output_file.close()


    """self.list_dicts_clusters_using_radii"""
    list_dict = self.list_dicts_clusters_using_radii
    counter = 1
    for index, item in enumerate(list_dict):
      output_file_path = str(self.csv_file).replace(".csv", "") + "__inputDL" + str(self.distance_levels) + "_02" + "___DL" + str(counter) + ".txt"
      output_file = open(output_file_path, "w")
      output_file.write("#calculated by g_list_dicts_of_clusters_using_radii()\n")    
      output_file.write("clusterID,pointIDs")    
      for key_clusterID in list_dict[index]:
        output_file.write("\n{},{}".format(key_clusterID, list_dict[index][key_clusterID]))
      output_file.close()
      counter += 1


    """self.dict_distancelevels_perID"""
    thisdict = self.dict_distancelevels_perID
    output_file_path = str(self.csv_file).replace(".csv", "") + "__inputDL" + str(self.distance_levels) + "_03" +  "___numDLperID" + ".txt"
    output_file = open(output_file_path, "w")
    output_file.write("#calculated by g_dict_number_of_distancelevels_perID()\n")    
    output_file.write("pointID,numOfDL")    
    for key in thisdict:
      output_file.write("\n{},{}".format(key, thisdict[key]))
    output_file.close()


    """self.dict_median_of_distancelevels_perID"""
    thisdict = self.dict_median_of_distancelevels_perID
    output_file_path = str(self.csv_file).replace(".csv", "") + "__inputDL" + str(self.distance_levels) + "_04" +  "___medianNumDLperID" + ".txt"
    output_file = open(output_file_path, "w")
    output_file.write("#calculated by g_dict_median_of_distancelevels_perID()\n")    
    output_file.write("pointID,medianOfDL")    
    for key in thisdict:
      output_file.write("\n{},{}".format(key, thisdict[key]))
    output_file.close()


    """self.dict_num_connections_across_DL"""
    thisdict = self.dict_num_connections_across_DL
    output_file_path = str(self.csv_file).replace(".csv", "") + "__inputDL" + str(self.distance_levels) +  "_05" + "___allConnectionsOnAllDLperID" + ".txt"
    output_file = open(output_file_path, "w")
    output_file.write("#calculated by g_sum_of_connections_across_distancelevels()\n")    
    output_file.write("pointID,allConnections")    
    for key in thisdict:
      output_file.write("\n{},{}".format(key, thisdict[key]))
    output_file.close()


    """self.g_dict_networkCentrality_ID"""
    thisdict = self.g_dict_networkCentrality_ID
    output_file_path = str(self.csv_file).replace(".csv", "") + "__inputDL" + str(self.distance_levels) + "_06" +  "___networkcentralityPerID" + ".txt"
    output_file = open(output_file_path, "w")
    output_file.write("#calculated by g_dict_networkCentrality_perID()\n")    
    output_file.write("pointID,NetworkCentrality")    
    for key in thisdict:
      output_file.write("\n{},{}".format(key, thisdict[key]))
    output_file.close()

  def write_only_selected(self, number = 6):
    switchdict = {
      "1" : "self.radii_list",
      "2" : "self.list_dicts_clusters_using_radii",
      "3" : "self.dict_distancelevels_perID",
      "4" : "self.dict_median_of_distancelevels_perID",
      "5" : "self.dict_num_connections_across_DL",
      "6" : "self.g_dict_networkCentrality_ID"
    }
    if ("int" in str(type(number))):
      if 1 <= number <= 6:
        numberstr = str(number)

        if numberstr == "1":
          """self.radii_list"""
          output_file_path =  str(self.csv_file).replace(".csv", "") + "__inputDL" + str(self.distance_levels) + "_01" + "___list_radii" + ".txt"
          output_file = open(output_file_path, "w")
          output_file.write("#radii calculated by g_list_radii()")    
          #--write rows
          for item in self.radii_list:
            output_file.write("\n{}".format(item))
          output_file.close()

        elif numberstr == "2":
          """self.list_dicts_clusters_using_radii"""
          list_dict = self.list_dicts_clusters_using_radii
          counter = 1
          for index, item in enumerate(list_dict):
            output_file_path = str(self.csv_file).replace(".csv", "") + "__inputDL" + str(self.distance_levels) + "_02" + "___DL" + str(counter) + ".txt"
            output_file = open(output_file_path, "w")
            output_file.write("#calculated by g_list_dicts_of_clusters_using_radii()\n")    
            output_file.write("clusterID,pointIDs")    
            for key_clusterID in list_dict[index]:
              output_file.write("\n{},{}".format(key_clusterID, list_dict[index][key_clusterID]))
            output_file.close()
            counter += 1

        elif numberstr == "3":
          """self.dict_distancelevels_perID"""
          thisdict = self.dict_distancelevels_perID
          output_file_path = str(self.csv_file).replace(".csv", "") + "__inputDL" + str(self.distance_levels) + "_03" +  "___numDLperID" + ".txt"
          output_file = open(output_file_path, "w")
          output_file.write("#calculated by g_dict_number_of_distancelevels_perID()\n")    
          output_file.write("pointID,numOfDL")    
          for key in thisdict:
            output_file.write("\n{},{}".format(key, thisdict[key]))
          output_file.close()

        elif numberstr == "4":
          """self.dict_median_of_distancelevels_perID"""
          thisdict = self.dict_median_of_distancelevels_perID
          output_file_path = str(self.csv_file).replace(".csv", "") + "__inputDL" + str(self.distance_levels) + "_04" +  "___medianNumDLperID" + ".txt"
          output_file = open(output_file_path, "w")
          output_file.write("#calculated by g_dict_median_of_distancelevels_perID()\n")    
          output_file.write("pointID,medianOfDL")    
          for key in thisdict:
            output_file.write("\n{},{}".format(key, thisdict[key]))
          output_file.close()

        elif numberstr == "5":
          """self.dict_num_connections_across_DL"""
          thisdict = self.dict_num_connections_across_DL
          output_file_path = str(self.csv_file).replace(".csv", "") + "__inputDL" + str(self.distance_levels) +  "_05" + "___allConnectionsOnAllDLperID" + ".txt"
          output_file = open(output_file_path, "w")
          output_file.write("#calculated by g_sum_of_connections_across_distancelevels()\n")    
          output_file.write("pointID,allConnections")    
          for key in thisdict:
            output_file.write("\n{},{}".format(key, thisdict[key]))
          output_file.close()

        elif numberstr == "6":
          """self.g_dict_networkCentrality_ID"""
          thisdict = self.g_dict_networkCentrality_ID
          output_file_path = str(self.csv_file).replace(".csv", "") + "__inputDL" + str(self.distance_levels) + "_06" +  "___networkcentralityPerID" + ".txt"
          output_file = open(output_file_path, "w")
          output_file.write("#calculated by g_dict_networkCentrality_perID()\n")    
          output_file.write("pointID,NetworkCentrality")    
          for key in thisdict:
            output_file.write("\n{},{}".format(key, thisdict[key]))
          output_file.close()

      else:
        print("please choose...")
        for key, value in switchdict.items():
          print("{} : {}".format(key, value))

    else:
      print("please choose...")
      for key, value in switchdict.items():
        print("{} : {}".format(key, value))

  def default_process(self):

    self.g_list_radii()
    self.g_list_dicts_of_clusters_using_radii()
    self.g_dict_number_of_distancelevels_perID()
    self.g_sum_of_connections_across_distancelevels()
    self.g_dict_networkCentrality_perID()

    #self.write_outputs_to_file()
