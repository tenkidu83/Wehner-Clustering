'''
Created on 20.05.2015

@author: Thomas Graichen (www.tgraichen.de)

'''

from ClusterBuilder_MarkIX import *

# new object
new_cluster = ClusterBuilder("1st_run/Archeod_select_filtered_DM.csv", 10)
new_cluster.default_process()
#new_cluster.write_outputs_to_file()
new_cluster.write_only_selected(1)

