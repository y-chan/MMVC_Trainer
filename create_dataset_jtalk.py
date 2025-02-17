import glob
import sys
import os
import argparse
import pyopenjtalk
import json

def mozi2phone(mozi):
    text = pyopenjtalk.g2p(mozi)
    text = "sil " + text + " sil"
    text = text.replace(' ', '-')
    return text

def create_json(filename, num_speakers, sr, config_path):
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    data['data']['training_files'] = 'filelists/' + filename + '_textful.txt'
    data['data']['validation_files'] = 'filelists/' + filename + '_textful_val.txt'
    data['data']['training_files_notext'] = 'filelists/' + filename + '_textless.txt'
    data['data']['validation_files_notext'] = 'filelists/' + filename + '_val_textless.txt'
    data['data']['sampling_rate'] = sr
    data['data']['n_speakers'] = num_speakers

    with open("./configs/" + filename + ".json", 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def create_dataset(filename):
    speaker_id = 0
    textful_dir_list = glob.glob("dataset/textful/*")
    textless_dir_list = glob.glob("dataset/textless/*")
    textful_dir_list.sort()
    textless_dir_list.sort()
    Correspondence_list = list()
    output_file_list = list()
    output_file_list_val = list()
    output_file_list_textless = list()
    output_file_list_val_textless = list()
    for d in textful_dir_list:
        wav_file_list = glob.glob(d+"/wav/*")
        lab_file_list = glob.glob(d + "/text/*")
        wav_file_list.sort()
        lab_file_list.sort()
        if len(wav_file_list) == 0:
            continue
        counter = 0
        for lab, wav in zip(lab_file_list, wav_file_list):
            with open(lab, 'r') as f:
                mozi = f.read().split("\n")
            print(str(mozi))
            test = mozi2phone(str(mozi))
            print(test)
            print(wav + "|"+ str(speaker_id) + "|"+ test)
            if counter % 10 != 0:
                output_file_list.append(wav + "|"+ str(speaker_id) + "|"+ test + "\n")
            else:
                output_file_list_val.append(wav + "|"+ str(speaker_id) + "|"+ test + "\n")
            counter = counter +1
        Correspondence_list.append(str(speaker_id)+"|"+os.path.basename(d) + "\n")
        speaker_id = speaker_id + 1

    for d in textless_dir_list:
        wav_file_list = glob.glob(d+"/*")
        wav_file_list.sort()
        counter = 0
        for wav in wav_file_list:
            print(wav + "|"+ str(speaker_id) + "|a")
            if counter % 10 != 0:
                output_file_list_textless.append(wav + "|"+ str(speaker_id) + "|a" + "\n")
            else:
                output_file_list_val_textless.append(wav + "|"+ str(speaker_id) + "|a" + "\n")
            counter = counter +1
        Correspondence_list.append(str(speaker_id)+"|"+os.path.basename(d) + "\n")
        speaker_id = speaker_id + 1

    with open('filelists/' + filename + '_textful.txt', 'w', encoding='utf-8', newline='\n') as f:
        f.writelines(output_file_list)
    with open('filelists/' + filename + '_textful_val.txt', 'w', encoding='utf-8', newline='\n') as f:
        f.writelines(output_file_list_val)
    with open('filelists/' + filename + '_textless.txt', 'w', encoding='utf-8', newline='\n') as f:
        f.writelines(output_file_list_textless)
    with open('filelists/' + filename + '_val_textless.txt', 'w', encoding='utf-8', newline='\n') as f:
        f.writelines(output_file_list_val_textless)
    with open('filelists/' + filename + '_Correspondence.txt', 'w', encoding='utf-8', newline='\n') as f:
        f.writelines(Correspondence_list)
    return speaker_id

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filename', type=str, required=True,
                        help='filelist for configuration')
    parser.add_argument('-s', '--sr', type=int, default=24000,
                        help='sampling rate (default = 24000)')
    parser.add_argument('-c', '--config', type=str, default="./configs/baseconfig.json",
                        help='JSON file for configuration')
    args = parser.parse_args()
    filename = args.filename
    print(filename)
    n_spk = create_dataset(filename)
    create_json(filename, n_spk, args.sr, args.config)

if __name__ == '__main__':
    main()