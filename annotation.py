import os
import pandas as pd
import argparse
import numpy as np

parser = argparse.ArgumentParser(description="Integrates the results of icatcher+, ffprobe, and ELAN for videos in the specified directory and outputs them to a csv file.")

parser.add_argument('-d','--dir', default='Sample')
args = parser.parse_args() 

homeDir = "./" # Change this directory as you like
ffprobeDir = homeDir + "OutputData/ffprobe/" + args.dir
ELANDir = homeDir + "InputData/ELAN/" + args.dir
ELANfiles = os.listdir(ELANDir)

outDir = homeDir + "OutputData/frame2time/" + args.dir
os.makedirs(outDir, exist_ok=True)

for tsvname in ELANfiles:

    if os.path.exists(os.path.join(ffprobeDir, tsvname)) & os.path.exists(os.path.join(ELANDir, tsvname)):
        ffprobefile = os.path.join(ffprobeDir, tsvname)
        ELANfile = os.path.join(ELANDir, tsvname)

        ffprobeDf = pd.read_csv(ffprobefile)
        frameNumber = len(ffprobeDf)
        newffprobeDf = ffprobeDf[4:(frameNumber-4)]
        newffprobeDf = newffprobeDf.reset_index(drop=True)

        gazeDf = pd.read_csv(ELANfile, delimiter='\t') #Assuming extra information is included at the top

        df = pd.DataFrame()

        #Since there were cases where pkt_duration information was clearly incorrect, pts_duration is used even if pkt_duration is detected
        df = pd.concat([newffprobeDf["pts_time"], newffprobeDf["pts_duration_time"]],axis=1)
        df = df.rename(columns={'pts_duration_time': 'duration_time'})

        ncol = gazeDf.shape[1]
        col = gazeDf.columns
        # human_annotation = ["NA"]*len(df) #Create an empty list of the same length as df
        human_annotation = np.empty((len(df), ncol-2))
        human_annotation[:, :] = np.nan
        human_annotation = human_annotation.astype(str)
        pts = np.array(df["pts_time"]) #Convert pts_time to a list
        
        # filename,frame,pts_time,duration_time,onset
        base_time = pd.to_datetime('00:00:0.0', format='%H:%M:%S.%f')
        gazeDf[col[0]]=(pd.to_datetime(gazeDf[col[0]], format='%H:%M:%S.%f') - base_time).dt.total_seconds()
        gazeDf[col[1]]=(pd.to_datetime(gazeDf[col[1]], format='%H:%M:%S.%f') - base_time).dt.total_seconds()
        
        for row in gazeDf.itertuples():

            start = row[1]
            end = row[2] #Contains a single value
            annotation = np.array([*row[3:]]).reshape(1, -1)

            #Calculate the difference between all elements of pts_time and start, and determine the starting point of human_annotation at the smallest point
            diff_start = np.array(pts - start)
            start_point = np.argmin(np.abs(diff_start))
            #Do the same for end to determine the end point
            diff_end = list(map(lambda x: x-end, pts))
            min_end = min(diff_end, key=abs)
            end_point = diff_end.index(min_end)
            
            #Tag everything in between with the same tag
            human_annotation[start_point:end_point+1, :] = np.repeat(annotation, end_point - start_point + 1, axis=0)
            
            #Then move to the next annotation
      
        haDf = pd.DataFrame(human_annotation, columns = col[2:])
        #Combine the information of ELAN's annotation
        df = pd.concat([df, haDf], axis=1)

        moviename = tsvname.replace('.txt', '.mp4')
        foldername = args.dir
        res = pd.DataFrame([[moviename]]*len(df)).join(df)
        res = res.rename(columns={0: 'filename'})
        res = pd.DataFrame([[foldername]]*len(res)).join(res)
        res = res.rename(columns={0: 'folder'})
        outputfile = os.path.join(outDir, tsvname)
        res.to_csv(outputfile, index=False)