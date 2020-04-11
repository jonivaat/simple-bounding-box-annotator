# -*- coding: utf-8 -*-
"""
Created on Wed May 22 16:03:20 2019

@author: Joni Väätäinen

Article from Adrian Rosebrock used as reference:
https://www.pyimagesearch.com/2015/03/09/capturing-mouse-click-events-with-python-and-opencv/
"""

# import the necessary packages
#import argparse
import os
import cv2
import numpy as np
import csv
import sys

images_dir = "./Images"
image_files = os.listdir(images_dir)
images = []
image_names = []
prev_state = 0
prev_state_a = 0
ann_var = 0 # avoid deleting more than one annotation at a time
end = False
edit_mode = False # modify latest bbox
edit_frame = 0 # save frame before edit started
prev_states_a = []
drag = False # represents long press in edit mode
tmp_rect = 0 # edit_mode parameter
corrected_boxes = []
for img_file in image_files:
    name, ext = os.path.splitext(img_file)
    assert ext == ".png" or ext == ".jpg", f"image extension is wrong! ({ext})"
    image_names.append(name)
    images.append(cv2.imread(os.path.join(images_dir,img_file)))
 
refPt = []
Pt_collection = []
rects = [] 

def click_event(event, x, y, flags, param):
    global refPt,Pt_collection, prev_state, prev_state_a
    global image, ann_var, prev_states_a, edit_mode, edit_frame, tmp_rect, drag, corrected_boxes
    
    
    if event == cv2.EVENT_MBUTTONDOWN:
        if len(rects) > 0:
            edit_mode = not(edit_mode)
            if edit_mode:
                edit_frame = prev_state_a.copy()
                print("edit mode activated")
                print(f"{'='*90}")
                tmp_rect = rects[-1]
            else:
                print(f"{'='*90}")
                print("edit mode deactivated")
                rects[-1] = tmp_rect
                box = cv2.boxPoints(tmp_rect)
                Pt_collection[-1] = box[3]
                Pt_collection[-2] = box[2]
                Pt_collection[-3] = box[1]
                Pt_collection[-4] = box[0]
                print(f"previous bbox altered! x: {round(rects[-1][0][0],2)}, y: {round(rects[-1][0][1],2)}," \
                      f"w: {round(rects[-1][1][0],2)}, h: {round(rects[-1][1][1],2)}, angle: {round(rects[-1][2],2)}")
        else:
            print("Cannot enter edit mode without any saved bboxes!")

    if not edit_mode:
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(refPt) == 0:
                prev_state = image.copy()
            refPt.append((x, y))
            cv2.circle(image,(x,y), 2, (255,0,0), -1)
            print(f"reference points x:{x} y:{y} saved")
            
        if event == cv2.EVENT_RBUTTONDOWN:
            if len(rects) > 0:
                prev_rect = rects[-1]
                rects.append(((x,y),(prev_rect[1][0],prev_rect[1][1]),prev_rect[2]))
                box = cv2.boxPoints(((np.int32(x),np.int32(y)),
                                     (np.int32(prev_rect[1][0]),np.int32(prev_rect[1][1])),
                                     np.int32(prev_rect[2])))
                Pt_collection.append(box[0])
                Pt_collection.append(box[1])
                Pt_collection.append(box[2])
                Pt_collection.append(box[3])
                if len(refPt) > 0:
                    image = prev_state.copy() # to hide the drawn "guiding dots"
                prev_state_a = image.copy()    
                prev_states_a.append(prev_state_a.copy())
                box = np.int32(box)
                cv2.drawContours(image,[box],0,(0,0,255),1)
                cv2.imshow("image", image)
                ann_var = 0
                refPt = []
                print(f"bbox saved! x: {round(x,2)}, y: {round(y,2)}, w: {round(prev_rect[1][0],2)}, h: {round(prev_rect[1][1],2)}, angle: {round(prev_rect[2],2)}")
            else:
                print("no previous bounding box saved!")
            
        if len(refPt) == 4:
            rect = np.stack(refPt)
            rect = cv2.minAreaRect(np.int32(rect))
            rects.append(rect)
            box = cv2.boxPoints(rect)
            Pt_collection.append(box[0])
            Pt_collection.append(box[1])
            Pt_collection.append(box[2])
            Pt_collection.append(box[3])
            box = np.int32(box)
            image = prev_state.copy() # to hide the drawn "guiding dots"
            prev_state_a = image.copy()
            prev_states_a.append(prev_state_a.copy())
            cv2.drawContours(image,[box],0,(0,0,255),1)
            prev_state = image.copy()
            cv2.imshow("image", image)
            print(f"bbox saved! x: {round(rect[0][0],2)}, y: {round(rect[0][1],2)}, w: {round(rect[1][0],2)}, h: {round(rect[1][1],2)}, angle: {round(rect[2],2)}")
            ann_var = 0
            refPt = []
            
    elif edit_mode:
        if event == cv2.EVENT_LBUTTONDOWN:
            tmp_rect = ((x,y),(tmp_rect[1][0],tmp_rect[1][1]),tmp_rect[2])
            sys.stdout.write(f"\r x: {round(tmp_rect[0][0],2)}, y: {round(tmp_rect[0][1],2)}, w: {round(tmp_rect[1][0],2)}, h: {round(tmp_rect[1][1],2)}, angle: {round(tmp_rect[2],2)}    ")
            sys.stdout.flush()
            box = cv2.boxPoints(tmp_rect)
            box = np.int32(box)
            image = edit_frame.copy()
            cv2.drawContours(image,[box],0,(0,0,255),1)
            cv2.imshow("image", image)
        if event == cv2.EVENT_MOUSEWHEEL:
            if flags == 7864320:
                tmp_rect = ((tmp_rect[0][0],tmp_rect[0][1]),
                            (tmp_rect[1][0],tmp_rect[1][1]),
                             tmp_rect[2]+2 if (tmp_rect[2]+2) <= 90 else 90)
            if flags == 15728640:
                tmp_rect = ((tmp_rect[0][0],tmp_rect[0][1]),
                            (tmp_rect[1][0],tmp_rect[1][1]),
                             tmp_rect[2]+4 if (tmp_rect[2]+4) <= 90 else 90)
            if flags == -7864320:
                tmp_rect = ((tmp_rect[0][0],tmp_rect[0][1]),
                            (tmp_rect[1][0],tmp_rect[1][1]),
                             tmp_rect[2]-2 if tmp_rect[2]-2 >= -90. else -90)
            if flags == -15728640:
                tmp_rect = ((tmp_rect[0][0],tmp_rect[0][1]),
                            (tmp_rect[1][0],tmp_rect[1][1]),
                             tmp_rect[2]-4 if tmp_rect[2]-4 >= -90. else -90)
            box = cv2.boxPoints(tmp_rect)
            box = np.int32(box)
            image = edit_frame.copy()
            cv2.drawContours(image,[box],0,(0,0,255),1)
            cv2.imshow("image", image)
            sys.stdout.write(f"\rx: {round(tmp_rect[0][0],2)}, y: {round(tmp_rect[0][1],2)}, w: {round(tmp_rect[1][0],2)}, h: {round(tmp_rect[1][1],2)}, angle: {round(tmp_rect[2],2)}    ")
            sys.stdout.flush()

if __name__ == "__main__":
    print(f"{'='*90}")
    print("# press 'a' to save bounding boxes to file and 'r' to reset image & bounding boxes")
    print("# press 'b' to delete only the latest ref. points and 'n' to delete latest bounding box and ref. points)")
    print("# press 's' to skip to next image and press 'q' or 'esc' to end program")  
    print("# press 'mouse l' to mark a reference point on image")
    print("# press 'mouse r' to copy the previous bounding box to cursors location")
    print("# press 'm' to activate/deactivate edit mode")
    print("# - in edit mode press 'mouse l' or arrow keys on numpad to move bbox")
    print("# - in edit mode press '7', '8' or 'mouse wheel' to rotate bbox")
    print("# - in edit mode press '*' or '/' to change width of bbox")
    print("# - in edit mode press '-' or '+' to change heigth of bbox")
    print(f"{'='*90}")
    
    # Main loop. Show images one at a time from the Images-folder
    for i,image in enumerate(images):
        if end: break
        print(f"Viewing image {i+1}/{len(images)}")
        clone = image.copy()
        prev_state = image.copy()
        prev_state_a = image.copy()
        prev_states_a = []
        cv2.namedWindow("image")
        cv2.setMouseCallback("image", click_event) 
        t = True
    
        while True and not end:

            cv2.imshow("image", image)
            key = cv2.waitKey(1) & 0xFF
            
            if len(Pt_collection) % 8  == 0 and len(Pt_collection) != 0 and t:
                t = False
            elif len(Pt_collection) % 8 != 0:
                t = True
            
            if key == ord("b") and len(refPt) > 0:
                image = prev_state.copy()
                refPt = []
                print("all reference points deleted!")
            if key == ord("n") and len(Pt_collection) > 0: #and not ann_var: 
                image = prev_states_a[-1].copy()
                prev_state = prev_states_a[-1].copy()
                del prev_states_a[-1]
                Pt_collection = Pt_collection[:-4] # delete the last for bbox points
                del rects[-1]
                ann_var = 1
                print("latest bounding box deleted!")               
                refPt = []
                print("all reference points deleted!")
         
            # if the 'r' key is pressed, reset all reference points and modifications
            if key == ord("r"):
                image = clone.copy()
                prev_state = clone.copy()
                prev_state_a = clone.copy()
                edit_frame = clone.copy()
                prev_states_a = []
                refPt = []
                Pt_collection = []
                rects = []
                edit_mode = False
                t = True
                print("image, bounding boxes and points reseted!")
            # if the 'a' key is pressed, save points and break the loop
            elif key == ord("a"):
                if len(Pt_collection) >= 4:
                    with open(f"./annotations/{image_names[i]}_annotations.txt",mode="w",newline="") as csv_file:  
                        csv_writer = csv.writer(csv_file, delimiter=" ")
                        for Pt in Pt_collection:
                            csv_writer.writerow(Pt)
                    print(f"bounding box(es) succesfully saved to path: ./annotations/{image_names[i]}_annotation.txt")                   
                else:
                    print(f"not enough annotations found ({len(Pt_collection)}). Moving to next image")
                image = clone.copy()
                prev_state = clone.copy()
                prev_state_a = clone.copy()
                edit_frame = clone.copy()
                prev_states_a = []
                refPt = []
                Pt_collection = []
                rects = []
                edit_mode = False
                break
                
            # Press 's' to skip to next image
            if key == ord('s'):
                print("moving to next image")
                image = clone.copy()
                prev_state = clone.copy()
                prev_state_a = clone.copy()
                edit_frame = clone.copy()
                prev_states_a = []
                refPt = []
                Pt_collection = []
                rects = []
                edit_mode = False
                break
                    
            # Press esc or 'q' to close the image window
            if key == ord('q') or key == 27:
                end = True
                break
############ EDIT MODE ##################
            if (key == ord("m") or key == 13):
                if len(rects) > 0:
                    edit_mode = not(edit_mode)
                    if edit_mode:
                        edit_frame = prev_state_a.copy()
                        print("edit mode activated")
                        print(f"{'='*90}")
                        tmp_rect = rects[-1]
                    else:
                        print(f"{'='*90}")
                        print("edit mode deactivated")
                        rects[-1] = tmp_rect
                        box = cv2.boxPoints(tmp_rect)
                        Pt_collection[-1] = box[3]
                        Pt_collection[-2] = box[2]
                        Pt_collection[-3] = box[1]
                        Pt_collection[-4] = box[0]
                        print(f"previous bbox altered! x: {round(rects[-1][0][0],2)}, y: {round(rects[-1][0][1],2)}," \
                              f"w: {round(rects[-1][1][0],2)}, h: {round(rects[-1][1][1],2)}, angle: {round(rects[-1][2],2)}")
                else:
                    print("Cannot enter edit mode without any saved bboxes!")
            # y+1
            if key == 56 and edit_mode:
                tmp_rect = ((tmp_rect[0][0],tmp_rect[0][1]-1),
                            (tmp_rect[1][0],tmp_rect[1][1]),
                             tmp_rect[2])
                box = cv2.boxPoints(tmp_rect)
                box = np.int32(box)
                image = edit_frame.copy()
                cv2.drawContours(image,[box],0,(0,0,255),1)
                cv2.imshow("image", image)
                sys.stdout.write(f"\rx: {round(tmp_rect[0][0],2)}, y: {round(tmp_rect[0][1],2)}, w: {round(tmp_rect[1][0],2)}, h: {round(tmp_rect[1][1],2)}, angle: {round(tmp_rect[2],2)}    ")
                sys.stdout.flush()
            # y-1
            if key == 50 and edit_mode:
                tmp_rect = ((tmp_rect[0][0],tmp_rect[0][1]+1),
                            (tmp_rect[1][0],tmp_rect[1][1]),
                             tmp_rect[2])
                box = cv2.boxPoints(tmp_rect)
                box = np.int32(box)
                
                image = edit_frame.copy()
                cv2.drawContours(image,[box],0,(0,0,255),1)
                cv2.imshow("image", image)
                sys.stdout.write(f"\rx: {round(tmp_rect[0][0],2)}, y: {round(tmp_rect[0][1],2)}, w: {round(tmp_rect[1][0],2)}, h: {round(tmp_rect[1][1],2)}, angle: {round(tmp_rect[2],2)}    ")
                sys.stdout.flush()
                
            # x+1
            if key == 54 and edit_mode: # button = "6"
                tmp_rect = ((tmp_rect[0][0]+1,tmp_rect[0][1]),
                            (tmp_rect[1][0],tmp_rect[1][1]),
                             tmp_rect[2])
                box = cv2.boxPoints(tmp_rect)
                box = np.int32(box)
                image = edit_frame.copy()
                cv2.drawContours(image,[box],0,(0,0,255),1)
                cv2.imshow("image", image)
                sys.stdout.write(f"\rx: {round(tmp_rect[0][0],2)}, y: {round(tmp_rect[0][1],2)}, w: {round(tmp_rect[1][0],2)}, h: {round(tmp_rect[1][1],2)}, angle: {round(tmp_rect[2],2)}    ")
                sys.stdout.flush()
            # x-1
            if key == 52 and edit_mode: # button = "-"
                tmp_rect = ((tmp_rect[0][0]-1,tmp_rect[0][1]),
                            (tmp_rect[1][0],tmp_rect[1][1]),
                             tmp_rect[2])
                box = cv2.boxPoints(tmp_rect)
                box = np.int32(box)
                image = edit_frame.copy()
                cv2.drawContours(image,[box],0,(0,0,255),1)
                cv2.imshow("image", image)
                sys.stdout.write(f"\rx: {round(tmp_rect[0][0],2)}, y: {round(tmp_rect[0][1],2)}, w: {round(tmp_rect[1][0],2)}, h: {round(tmp_rect[1][1],2)}, angle: {round(tmp_rect[2],2)}    ")
                sys.stdout.flush()
            
            # width+1
            if key == 47 and edit_mode:# button = "/"
                tmp_rect = ((tmp_rect[0][0],tmp_rect[0][1]),
                            (tmp_rect[1][0]+1,tmp_rect[1][1]),
                             tmp_rect[2])
                sys.stdout.write(f"\rparameters: x: {round(tmp_rect[0][0],2)}, y: {round(tmp_rect[0][1],2)}, w: {round(tmp_rect[1][0],2)}, h: {round(tmp_rect[1][1],2)}, angle: {round(tmp_rect[2],2)}    ")
                sys.stdout.flush()
                box = cv2.boxPoints(tmp_rect)
                box = np.int32(box)
                image = edit_frame.copy()
                cv2.drawContours(image,[box],0,(0,0,255),1)
            # width-1    
            if key == 42 and edit_mode: # button = "*"
                tmp_rect = ((tmp_rect[0][0],tmp_rect[0][1]),
                            (tmp_rect[1][0]-1,tmp_rect[1][1]),
                             tmp_rect[2])
                sys.stdout.write(f"\rparameters: x: {round(tmp_rect[0][0],2)}, y: {round(tmp_rect[0][1],2)}, w: {round(tmp_rect[1][0],2)}, h: {round(tmp_rect[1][1],2)}, angle: {round(tmp_rect[2],2)}    ")
                sys.stdout.flush()
                box = cv2.boxPoints(tmp_rect)
                box = np.int32(box)
                image = edit_frame.copy()
                cv2.drawContours(image,[box],0,(0,0,255),1)
                
            # height+1
            if key == 43 and edit_mode: # button = "+"
                tmp_rect = ((tmp_rect[0][0],tmp_rect[0][1]),
                            (tmp_rect[1][0],tmp_rect[1][1]+1),
                             tmp_rect[2])
                sys.stdout.write(f"\rparameters: x: {round(tmp_rect[0][0],2)}, y: {round(tmp_rect[0][1],2)}, w: {round(tmp_rect[1][0],2)}, h: {round(tmp_rect[1][1],2)}, angle: {round(tmp_rect[2],2)}    ")
                sys.stdout.flush()
                box = cv2.boxPoints(tmp_rect)
                box = np.int32(box)
                image = edit_frame.copy()
                cv2.drawContours(image,[box],0,(0,0,255),1)
            # height-1    
            if key == 45 and edit_mode: # button = "-"
                tmp_rect = ((tmp_rect[0][0],tmp_rect[0][1]),
                            (tmp_rect[1][0],tmp_rect[1][1]-1),
                             tmp_rect[2])
                sys.stdout.write(f"\rparameters: x: {round(tmp_rect[0][0],2)}, y: {round(tmp_rect[0][1],2)}, w: {round(tmp_rect[1][0],2)}, h: {round(tmp_rect[1][1],2)}, angle: {round(tmp_rect[2],2)}    ")
                sys.stdout.flush()
                box = cv2.boxPoints(tmp_rect)
                box = np.int32(box)
                image = edit_frame.copy()
                cv2.drawContours(image,[box],0,(0,0,255),1)
                
            # angle+1
            if key == 55 and edit_mode: # button = "7"
                tmp_rect = ((tmp_rect[0][0],tmp_rect[0][1]),
                            (tmp_rect[1][0],tmp_rect[1][1]),
                             tmp_rect[2]+1 if (tmp_rect[2]+1) <= 90 else tmp_rect[2])
                sys.stdout.write(f"\rparameters: x: {round(tmp_rect[0][0],2)}, y: {round(tmp_rect[0][1],2)}, w: {round(tmp_rect[1][0],2)}, h: {round(tmp_rect[1][1],2)}, angle: {round(tmp_rect[2],2)}    ")
                sys.stdout.flush()
                box = cv2.boxPoints(tmp_rect)
                box = np.int32(box)
                image = edit_frame.copy()
                cv2.drawContours(image,[box],0,(0,0,255),1)
            # angle-1    
            if key == 57 and edit_mode: # button = "9"
                tmp_rect = ((tmp_rect[0][0],tmp_rect[0][1]),
                            (tmp_rect[1][0],tmp_rect[1][1]),
                             tmp_rect[2]-1 if tmp_rect[2]-1 >= -90. else tmp_rect[2])
                sys.stdout.write(f"\rparameters: x: {round(tmp_rect[0][0],2)}, y: {round(tmp_rect[0][1],2)}, w: {round(tmp_rect[1][0],2)}, h: {round(tmp_rect[1][1],2)}, angle: {round(tmp_rect[2],2)}    ")
                sys.stdout.flush()
                box = cv2.boxPoints(tmp_rect)
                box = np.int32(box)
                image = edit_frame.copy()
                cv2.drawContours(image,[box],0,(0,0,255),1)
                
    print("exiting program!")
    cv2.destroyAllWindows()                    