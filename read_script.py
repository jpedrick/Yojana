#!/usr/bin/env python3
"""
  Copyright notice:
  This file is part of Cursed.
  Cursed is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  Cursed is also covered by GNU Affero General Public License with the 
  following permission under the GNU Affero GPL version 3 section 7:
      If you modify this Program, or any covered work, by linking or
      combining it with other code, such other code is not for that reason
      alone subject to any of the requirements of the GNU Affero GPL
      version 3.

  Cursed is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with Cursed.  If not, see <https://www.gnu.org/licenses/>.

  You should also have received a copy of the GNU Affero General Public License
  along with Cursed.  If not, see <https://www.gnu.org/licenses/>.
"""
import sys, os, argparse, hashlib, json, time, io

import requests
import urllib
from AnywhereFile import AnywhereFile

from pydub import AudioSegment
import num2words
from gtts import gTTS
from num2words import num2words

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

speech_dict = {} 
sound_dict = {}

devnull = open(os.devnull, 'w')
cache_dir = os.path.expanduser('~') + "/.yojana/cache"
script_dir = '.'

pygame.mixer.pre_init()
pygame.mixer.init()
pygame.init()

sound_channel = pygame.mixer.find_channel()

def wait_until( t ):
    while( t > time.time() ):
        time.sleep(0.1)

def play_music(music_file, volume=0.8):
    if music_file not in sound_dict:
        f = AnywhereFile( music_file )
        sound_dict[music_file] = pygame.mixer.Sound( AudioSegment.from_mp3( f.data ).export( format = 'ogg' ) )
    try:
        sound_channel.set_volume( volume )
        sound_channel.queue( sound_dict[music_file] )
        while sound_channel.get_busy():
            time.sleep(0.1)
    except Exception as e:
        print("File {} not found! {}".format(music_file, str(e) ))
        return

def cache_words( words, cache_dir, voice = "en-in" ):
    words_hash = hashlib.md5( words.encode() ).hexdigest()
    c_path = '/'.join( [ cache_dir, words_hash + '.' + voice + '.mp3' ] )
    if words not in speech_dict:
        if os.path.exists( c_path ):
            speech_dict[ words ] = c_path
        else:
            gwav = gTTS( words, voice )
            speech_dict[ words ] = c_path
            error = gwav.save( c_path )
            speech_dict[ words ] = c_path
            time.sleep(0.1)
    return speech_dict[ words ]

def say_now( words, voice ):
    sys.stdout.flush()

    play_music( cache_words( words, cache_dir, voice=voice ) )

def do_sequence( sequence, script, start_at = 0 ):
    voice = script["speech_settings"]["voice"]
    end_et = time.time()

    for i in sequence:
        if start_at > 0:
            start_at = start_at - 1
            continue

        if "id" in i:
            print( str(i["id"]) + ":", end = ' ' )

        if "sequence" in i:
            do_sequence( script["sequences"][ i["sequence"] ], script )
        else:
            n_t = time.time()
            if "duration" in i:
                end_et = i["duration"] + n_t

            if "sound" in i:
                print('play sound: ', i["sound"] )
                play_music( '/'.join( [ script_dir, i["sound"] ] ) )
                wait_until( end_et )
            elif "speech"  in i:
                print( i["speech"] )
                say_now(i["speech"], voice )
                wait_until( end_et )
            elif "sequences" in i:
                for seq in i["sequences"]:
                    do_sequence( script["sequences"][ seq ], script )
            elif "count_up"  in i:
                print( "count up: ", end = ' ' )
                for n in range(1, i["count_up"] + 1, 1):
                    n_t = time.time()
                    print( num2words(n), end = ' ' )
                    say_now(num2words(n), voice )
                    wait_until( n_t + i["duration"])
                print( )
            elif "count_down"  in i:
                print( "count down: ", end = ' ' )
                for n in range(i["count_down"],0, -1):
                    n_t = time.time()
                    print( num2words(n), end = ' ' )
                    say_now(num2words(n), voice )
                    wait_until( n_t + i["duration"])
                print( )
            elif "skip_count_down"  in i:
                print( "skip count down: ", end = ' ' )
                for n in range( i["skip_count_down"], 0, -i["duration"] ):
                    n_t = time.time()
                    print( num2words(n), end = ' ' )
                    say_now(num2words(n), voice )
                    wait_until( n_t + i["duration"])
                say_now("done", voice )
                print( )
            elif "stop":
                say_now("stop", voice )
                return

parser = argparse.ArgumentParser( description='Script reader' )
parser.add_argument( 'script', type=str )
parser.add_argument( '--voice', type=str )
parser.add_argument( '--skip', type=int )
args = parser.parse_args()

script_file = AnywhereFile( args.script )

if True:
    script_dir = os.path.dirname( args.script )
    print( "script root:", script_dir )

    script = json.load( script_file.data )
    voice = "en-in"

    if not os.path.exists( cache_dir ):
        try:
            os.makedirs(cache_dir)
        except OSError:
            print( "Unable to make cache directory %s" % cache_dir )
            sys.exit()

    if "speech_settings" in script:
        for k, v in script["speech_settings"].items():
            if "voice" == k:
                voice = v
                if args.voice:
                    voice = args.voice
    print( "voice:", voice )

    #cache some numbers
    for n in range( 10, 0, -1):
        cache_words( num2words(n), cache_dir, voice=voice )

    for n in [ 15, 30, 45, 60 ]:
        cache_words( num2words(n), cache_dir, voice=voice )

    if "script" in script:
        for i in script["script"]:
            if "speech"  in i:
                cache_words(i["speech"], cache_dir, voice=voice)

    if "script" in script:
        start_at = 0
        if args.skip:
            start_at = args.skip

        do_sequence( script["script"], script, start_at=start_at )


