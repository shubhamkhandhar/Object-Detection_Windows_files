import dropbox
import os

destination_test = '/home/pi/tensorflow1/models-master/research/object_detection/KJSCE_Model/'
filelist = [ f for f in os.listdir(destination_test) if f.endswith(".pb") ]
for f in filelist:
    os.remove(os.path.join(destination_test, f))
access_token = 'oG7g0mYYCfAAAAAAAAAAD71siPToPbfzNVclK-9lY-jDzYahVep2AGKFXymw8jC3'
dbx = dropbox.Dropbox(access_token)                    
f = open("frozen_inference_graph.pb","wb")
#metadata,res = dbx.files_download("/home/pi/tensorflow1/models-master/research/object_detection/KJSCE_Model/frozen_inference_graph.pb")
metadata,res = dbx.files_download("/frozen_inference_graph.pb") 
f.write(res.content)