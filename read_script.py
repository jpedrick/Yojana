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
music_dict = {}

devnull = open(os.devnull, 'w')
cache_dir = os.path.expanduser('~') + "/.yojana/cache"
script_dir = '.'

pygame.mixer.pre_init()
pygame.mixer.init()
pygame.init()
screen = pygame.display.set_mode((350, 950))
font = pygame.font.Font( None, 36 )
background = pygame.Surface( screen.get_size() )
background = background.convert()
background.fill((250, 250, 250))

sound_channel = pygame.mixer.Channel(0)
music_channel = pygame.mixer.Channel(1)

def wait_until( t ):
    while( t > time.time() ):
        time.sleep(0.1)

def play_music(music_file, volume):
    if music_file not in music_dict:
        f = AnywhereFile( music_file )
        music_dict[music_file] = pygame.mixer.Sound( AudioSegment.from_mp3( f.data ).export( format = 'ogg' ) )
    try:
        sound_channel.set_volume( volume )
        sound_channel.queue( sound_dict[music_file] )
    except Exception as e:
        print("File {} not found! {}".format(music_file, str(e) ))
        return

def play_sound(sound_file, volume):
    if sound_file not in sound_dict:
        f = AnywhereFile( sound_file )
        sound_dict[sound_file] = pygame.mixer.Sound( AudioSegment.from_mp3( f.data ).export( format = 'ogg' ) )
    try:
        sound_channel.set_volume( volume )
        sound_channel.queue( sound_dict[sound_file] )
        while sound_channel.get_busy():
            time.sleep(0.1)
    except Exception as e:
        print("File {} not found! {}".format(sound_file, str(e) ))
        return

def play_words(sound_file, volume):
    if sound_file not in sound_dict:
        f = AnywhereFile( sound_file )
        sound_dict[sound_file] = pygame.mixer.Sound( AudioSegment.from_mp3( f.data ).export( format = 'ogg' ) )
    try:
        sound_channel.set_volume( volume )
        sound_channel.queue( sound_dict[sound_file] )
    except Exception as e:
        print("File {} not found! {}".format(sound_file, str(e) ))
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


# draw some text into an area of a surface
# automatically wraps words
# returns any text that didn't get blitted
# this function was copied from: https://www.pygame.org/wiki/TextWrap
def drawText(surface, text, color, rect, font, aa=False, bkg=None):
    rect = pygame.Rect(rect)
    y = rect.top
    lineSpacing = -2

    # get the height of the font
    fontHeight = font.size("Tg")[1]

    while text:
        i = 1

        # determine if the row of text will be outside our area
        if y + fontHeight > rect.bottom:
            break

        # determine maximum width of line
        while font.size(text[:i])[0] < rect.width and i < len(text):
            i += 1

        # if we've wrapped the text, then adjust the wrap to the last word      
        if i < len(text): 
            i = text.rfind(" ", 0, i) + 1

        # render the line and blit it to the surface
        if bkg:
            image = font.render(text[:i], 1, color, bkg)
            image.set_colorkey(bkg)
        else:
            image = font.render(text[:i], aa, color)

        surface.blit(image, (rect.left, y))
        y += fontHeight + lineSpacing

        # remove the text we just blitted
        text = text[i:]

    return text

def say_now( words, voice, volume ):
    play_words( cache_words( words, cache_dir, voice=voice ), volume )

    background.fill( (0, 10, 40) )
    drawText( background, words, (250, 20, 20), background.get_rect(), font, aa=True )
    screen.blit( background, (0,0) )
    pygame.display.flip()

    while sound_channel.get_busy():
        time.sleep(0.1)

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
                play_sound( '/'.join( [ script_dir, i["sound"] ] ), volume = i.get( "volume", 1 ) )
                wait_until( end_et )
            elif "music" in i:
                print('play music: ', i["song"] )
                play_music( '/'.join( [ script_dir, i["song"] ] ), volume = i.get( "volume", 1 ) )
            elif "speech"  in i:
                print( i["speech"] )
                say_now(i["speech"], voice, volume = i.get( "volume", 1 ) )
                wait_until( end_et )
            elif "sequences" in i:
                for seq in i["sequences"]:
                    do_sequence( script["sequences"][ seq ], script )
            elif "count_up"  in i:
                print( "count up: ", end = ' ' )
                for n in range(1, i["count_up"] + 1, 1):
                    n_t = time.time()
                    print( num2words(n), end = ' ' )
                    say_now(num2words(n), voice, volume = i.get( "volume", 1 ) )
                    wait_until( n_t + i["duration"])
                print( )
            elif "count_down"  in i:
                print( "count down: ", end = ' ' )
                for n in range(i["count_down"],0, -1):
                    n_t = time.time()
                    print( num2words(n), end = ' ' )
                    say_now(num2words(n), voice, volume = i.get( "volume", 1 ) )
                    wait_until( n_t + i["duration"])
                print( )
            elif "skip_count_down"  in i:
                print( "skip count down: ", end = ' ' )
                for n in range( i["skip_count_down"], 0, -i["duration"] ):
                    n_t = time.time()
                    print( num2words(n), end = ' ' )
                    say_now(num2words(n), voice, volume = i.get( "volume", 1 ) )
                    wait_until( n_t + i["duration"])
                say_now("done", voice )
                print( )
            elif "stop":
                say_now("stop", voice, volume = i.get( "volume", 1 ) )
                return

parser = argparse.ArgumentParser( description='Script reader' )
parser.add_argument( 'script', type=str )
parser.add_argument( '--voice', type=str )
parser.add_argument( '--skip', type=int )
args = parser.parse_args()

script_file = AnywhereFile( args.script )

if True:
    pygame.display.set_caption( f'Yojana: {args.script}' )
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


