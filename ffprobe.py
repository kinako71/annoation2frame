import subprocess
import pandas as pd
import os
import argparse
import ffmpeg

parser = argparse.ArgumentParser(description="Outputs pts/pts_time/pkt_duration_time in CSV format for all videos in the specified directory")

parser.add_argument('-d','--dir', default='Sample')
args = parser.parse_args() 

homeDir = "./" # Change this directory as you like
inputDir = homeDir + "InputData/Video/" + args.dir
inputfiles = os.listdir(inputDir)
outDir = homeDir + "OutputData/ffprobe/" + args.dir
os.makedirs(outDir, exist_ok=True)

for inputfile in inputfiles:
    targetfile = os.path.join(inputDir, inputfile)
    jsonfile = os.path.join(outDir, inputfile.replace('.mp4', '.json'))
    csvfile = os.path.join(outDir, inputfile.replace('.mp4', '.txt'))
    command = 'ffprobe -show_frames -select_streams v -print_format json "{}" > {}'.format(targetfile, jsonfile)

    try:
        # コマンドを実行して結果をCompletedProcessオブジェクトとして取得
        response = subprocess.run(
            command, # 実行するコマンド
            shell=True, # shell上で実行
            check=True, # 終了コードが非ゼロの場合CalledProcessErrorをraise
            stdout=subprocess.PIPE, # 処理結果をPIPEに渡す
        )

    except subprocess.CalledProcessError as e:
        raise e


    #変換したいJSONファイルを読み込む
    df = pd.read_json(jsonfile)

    # read_jsonした結果だとネストしたjsonを展開できないのでnormalizeで展開させる
    df_json = pd.json_normalize(df['frames'])

    if "pkt_duration_time" in df_json.columns:
        df_csv = df_json[["pts","pts_time","pkt_duration_time"]].copy()
    else:
        df_csv = df_json[["pts","pts_time"]].copy()
        df_csv["pkt_duration_time"] = "NaN"

    #pkt_duration_time2 次のpts_timeとの差分
    df_csv["pts_duration_time"] = ""
    for i, row in df_csv.iterrows():
        if i == len(df_csv)-1:
            probe = ffmpeg.probe(targetfile)
            endtime = probe['format']['duration']
            duration = float(endtime) - float(df_csv.at[i, 'pts_time'])
        else:
            duration = float(df_csv.at[i+1, 'pts_time']) - float(df_csv.at[i, 'pts_time'])
        
        duration = '{:.6f}'.format(duration)
        df_csv.at[i, 'pts_duration_time'] = duration

    df_csv[df_csv['pts_duration_time'] != "0.000000"].to_csv(csvfile, encoding='utf-8', index=False)
    
