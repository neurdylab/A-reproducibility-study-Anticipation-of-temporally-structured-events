
# import the modules
import os
import sys # to access the system
import cv2

# get the path/directory
folder_dir = "/media/bayrakrg/digbata2/anticipation/processed_data/"
for folder in os.listdir(folder_dir):
    if '.feat' in folder:
        # check if the image ends with png
        file = folder.strip('proc.feat') + "QA_image.png"
        img = cv2.imread(os.path.join(folder_dir, folder, file), cv2.IMREAD_ANYCOLOR)

        try:
            cv2.imshow(file, img)
            cv2.waitKey(0)          
            cv2.destroyAllWindows()
            cv2.waitKey(1)
        except:
            print(f"""Failed to open and or view {file}""")