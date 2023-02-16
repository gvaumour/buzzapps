import os
import argparse
import youtube_dl
from pydub import AudioSegment

def get_youtube_mp3(url):
    video_info = youtube_dl.YoutubeDL().extract_info(
        url = url,download=False
    )
    filename = f"{video_info['title']}.mp3"
    options={
        'format':'bestaudio/best',
        'keepvideo':False,
        'outtmpl':filename,
    }

    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download([video_info['webpage_url']])

    print("Download complete... {}".format(filename))
    return filename

# Convert 1:15 time to 75000ms 
def convert_to_millis(time):
    split_str = time.split(':')
    if len(split_str) == 2:
        return (60*int(split_str[0]) + int(split_str[1]))*1000
    return 0
            

def split_audio_file(mp3_filename, start, end, song, output_dir):

    print(mp3_filename)
    sound = AudioSegment.from_file(mp3_filename)
    
    ms_start = convert_to_millis(start)
    ms_end = convert_to_millis(end)
    if (ms_start > ms_end):
        print("Pb with time sample")
        return "" 
    elif (ms_end == 0):
        print("End sample is 0 ?? ")
        return "" 
        
    # We get the sample from the full video
    sample = sound[ms_start:ms_end]

    # We build a filename based on the 10 first letter of the song 
    sample_filename = "".join(ch for ch in song.strip() if ch.isalnum())
    sample_filename = sample_filename[:10:] + ".mp3"
    print(sample_filename)
    sample.export(os.path.join(output_dir, sample_filename), format="mp3")

    return sample_filename

def parse_playlist_file(playlist_filename, output_dir):
    f = open(playlist_filename, "r")
    lines = f.readlines()

    output_file = open(os.path.join(output_dir, "round.txt") , "w")

    for line in lines: 
        if not line:
            return
        split_line = line.split('\t')
        print(split_line)
        if len(split_line) != 5:
            continue

        url = split_line[0]
        start = split_line[1]
        end = split_line[2]
        author = split_line[3]
        song = split_line[4].strip()

        mp3_filename = get_youtube_mp3(url)
        sample_filename = split_audio_file(mp3_filename, start, end, song, output_dir)
        if sample_filename != "":
            output_file.write(author + "\t" + song + "\t" + sample_filename)
    
    output_file.close()
 
parser = argparse.ArgumentParser()
parser.add_argument("-o", "--output", help = "")
parser.add_argument("-p", "--playlist", help = "Playlist file")
 
args = parser.parse_args()
 
if not args.playlist:
    print("Mss the playlist file -f option")
elif not args.output:
    print("Miss the output dir -o option")
else:
    parse_playlist_file(args.playlist, args.output)