#!/usr/bin/env python3
import sys, os, argparse, hashlib, json, subprocess, time, io

import num2words
from gtts import gTTS
from num2words import num2words

speech_dict = {}
devnull = open(os.devnull, 'w')

def wait_until( t ):
    while( t > time.time() ):
        time.sleep(0.1)

def play_music(music_file, volume=0.8):
    '''
    stream music with mixer.music module in a blocking manner
    this will stream the sound from disk while playing
    '''
    # set up the mixer
    #freq = 44100     # audio CD quality
    #bitsize = -16    # unsigned 16 bit
    #channels = 2     # 1 is mono, 2 is stereo
    #buffer = 2048    # number of samples (experiment to get best sound)
    # volume value 0.0 to 1.0
    try:
        subprocess.run( ["play", "--type", "mp3", "--volume", str(volume), '-V1', music_file ], stdout=devnull, stderr=devnull )
    except Exception as e:
        print("File {} not found! {}".format(music_file, str(e) ))
        return

def cache_words( words, cache_dir='./', voice = "en-in" ):
    words_hash = hashlib.md5( words.encode() ).hexdigest()
    c_path = cache_dir + words_hash + '.' + voice + '.mp3' 
    if words not in speech_dict:
        if os.path.exists( c_path ):
            speech_dict[ words ] = c_path
        else:
            gwav = gTTS( words, voice )
            speech_dict[ words ] = c_path
            error = gwav.save( c_path )
            speech_dict[ words ] = c_path
            time.sleep(0.1)
            print( "saved \"", words, "\" to:", speech_dict[words], " with error: ", error )
    return speech_dict[ words ]

def say_now( words, voice ):
    print( words, end = ' ' )
    sys.stdout.flush()

    play_music( cache_words( words, voice=voice ) )

def do_sequence( sequence, script, start_at = 0 ):
    voice = script["speech_settings"]["voice"]
    end_et = time.time()

    for i in sequence:
        if start_at > 0:
            start_at = start_at - 1
            continue
        print()
        if "sequence" in i:
            do_sequence( script["sequences"][ i["sequence"] ], script )
        else:
            n_t = time.time()
            if "duration" in i:
                end_et = i["duration"] + n_t

            if "sound" in i:
                print('play sound: ', i["sound"], end=' ' )
                play_music(i["sound"])
                wait_until( end_et )
            elif "speech"  in i:
                say_now(i["speech"], voice )
                wait_until( end_et )
            elif "count_up"  in i:
                print( "count up: ", end = ' ' )
                for n in range(1, i["count_up"] + 1, 1):
                    n_t = time.time()
                    say_now(num2words(n), voice )
                    wait_until( n_t + i["duration"])
            elif "count_down"  in i:
                print( "count down: ", end = ' ' )
                for n in range(i["count_down"],0, -1):
                    n_t = time.time()
                    say_now(num2words(n), voice )
                    wait_until( n_t + i["duration"])
            elif "skip_count_down"  in i:
                print( "skip count down: ", end = ' ' )
                for n in range( i["skip_count_down"], 0, -i["duration"] ):
                    n_t = time.time()
                    say_now(num2words(n), voice )
                    wait_until( n_t + i["duration"])
                say_now("done", voice )
            elif "stop":
                say_now("stop", voice )
                return

parser = argparse.ArgumentParser( description='Script reader' )
parser.add_argument( 'script', type=str )
parser.add_argument( '--skip', type=int )
args = parser.parse_args()

with open( args.script ) as script_file:
    script = json.load( script_file )
    voice = script["speech_settings"]["voice"]

    if script["speech_settings"]:
        for k, v in script["speech_settings"].items():
            print( k, v )
    print("precaching speech")
    for n in range( 10, 0, -1):
        cache_words( num2words(n), voice=voice )

    if "script" in script:
        for i in script["script"]:
            if "speech"  in i:
                cache_words(i["speech"], voice=voice)

    for n in [ 15, 30, 45, 60 ]:
        cache_words( num2words(n), voice=voice )

    if "script" in script:
        do_sequence( script["script"], script, start_at=args.skip )


