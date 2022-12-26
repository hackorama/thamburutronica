# Convert to low res files accepted by circuitpython audiocore

IN=tanpura.mp3
OUT_MP3=${IN%.*}_lo.mp3
OUT_WAV=${IN%.*}_lo.wav

# 32k        bit rate
# -ac        1 for  mono, 2 for sterio
# -ar 44100  sampling rate in hz
ffmpeg -i $IN -codec:a libmp3lame -b:a 16k -ac 1 -ar 16000 TEMP_$OUT_MP3

# add half second silence
sox TEMP_$OUT_MP3 $OUT_MP3 pad 0.5 0
# trim first five seconds
#sox TEMP_$OUT_MP3 $OUT_MP3 pad trim  5
# trim first  and last five seconds
#sox TEMP_$OUT_MP3 $OUT_MP3 pad trim  5 -5

sox $IN -c 1 -b 16 -r 16000 $OUT_WAV

# pcm_s16le 16 bit
ffmpeg -i $IN -acodec pcm_s16le -ac 1 -ar 16000 $OUT_WAV

# check level
ffmpeg -i $IN  -filter:a volumedetect -f null /dev/null

ffprobe  $IN
ffprobe  $OUT_MP3
ffprobe  $OUT_WAV
du -h $IN
du -h $OUT_MP3
du -h $OT_WAV
