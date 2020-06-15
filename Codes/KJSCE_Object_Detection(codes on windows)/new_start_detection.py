import os
from random import choice
import shutil 
def main():
    # Function to move all files in same folder
    source = 'C:/Users/Admin/Desktop/KJSCE_Object_Detection/Img Files'
    source1 = 'C:/Users/Admin/Desktop/KJSCE_Object_Detection/XML Files'
    destination = 'C:/Users/Admin/Desktop/KJSCE_Object_Detection/models/research/object_detection/images/images1'
    # If folder contains previous files it will remove them all
    filelist = [ f for f in os.listdir(destination) if f.endswith(".jpeg") ]
    for f in filelist:
        os.remove(os.path.join(destination, f))
    filelist1 = [ f for f in os.listdir(destination) if f.endswith(".xml") ]
    for f in filelist1:
        os.remove(os.path.join(destination, f))
    #Starting Moving 
    files = os.listdir(source)
    files1 = os.listdir(source1)
    for f in files:
        dest = shutil.move(source+'\\'+f, destination)
    for f in files1:
        dest = shutil.move(source1+'\\'+f, destination)

    # Function to delete all previous .jpg and .xml files in train folder
    destination_train = 'C:/Users/Admin/Desktop/KJSCE_Object_Detection/models/research/object_detection/images/train'
    filelist = [ f for f in os.listdir(destination_train) if f.endswith(".jpeg") ]
    for f in filelist:
        os.remove(os.path.join(destination_train, f))
    filelist1 = [ f for f in os.listdir(destination_train) if f.endswith(".xml") ]
    for f in filelist1:
        os.remove(os.path.join(destination_train, f))


    # Function to delete all previous .jpg and .xml files in test folder
    destination_test = 'C:/Users/Admin/Desktop/KJSCE_Object_Detection/models/research/object_detection/images/test'
    filelist = [ f for f in os.listdir(destination_test) if f.endswith(".jpeg") ]
    for f in filelist:
        os.remove(os.path.join(destination_test, f))
    filelist1 = [ f for f in os.listdir(destination_test) if f.endswith(".xml") ]
    for f in filelist1:
        os.remove(os.path.join(destination_test, f))


    os.chdir('C:\\') #Make sure you add your source and destination path below
 # copy all files in train folder
    dir_src = ("C:\\Users\\Admin\\Desktop\\KJSCE_Object_Detection\\models\\research\\object_detection\\images\\images1\\")
    dir_dst = ("C:\\Users\\Admin\\Desktop\\KJSCE_Object_Detection\\models\\research\\object_detection\\images\\train\\")

    for filename in os.listdir(dir_src):
        if filename.endswith('.jpeg'):
            shutil.copy( dir_src + filename, dir_dst)
        print(filename)
        if filename.endswith('.xml'):
            shutil.copy( dir_src + filename, dir_dst)
        print(filename)

        
 # copy all files in test folder
    dir_dst_test = ("C:\\Users\\Admin\\Desktop\\KJSCE_Object_Detection\\models\\research\\object_detection\\images\\test\\")
    for filename in os.listdir(dir_src):
        if filename.endswith('.jpeg'):
            shutil.copy( dir_src + filename, dir_dst_test)
        print(filename)
        if filename.endswith('.xml'):
            shutil.copy( dir_src + filename, dir_dst_test)
        print(filename)


    #Function to remove previous .csv file from the folder
    destination_remove_csv = 'C:/Users/Admin/Desktop/KJSCE_Object_Detection/models/research/object_detection/images'
    filelist = [ f for f in os.listdir(destination_remove_csv) if f.endswith(".csv") ]
    for f in filelist:
        os.remove(os.path.join(destination_remove_csv, f))




if __name__ == '__main__': 
      
    # Calling main() function 
    main()

    
