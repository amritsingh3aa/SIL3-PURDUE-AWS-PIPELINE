from pkg_resources import require
import textgrids
import re
from utoken import utokenize
import os
from pydub import AudioSegment
import pandas as pd
import time
import clearml
from clearml import Task
from clearml import Dataset
import argparse

Task.add_requirements('-rrequirements.txt')
task = Task.init(
      project_name='IDX_Nathan_Internship',    # project name of at least 3 characters
      task_name='tts-mfa-to-coqui-' + str(int(time.time())), # task name of at least 3 characters
      task_type="training",
      tags=None,
      reuse_last_task_id=True,
      continue_last_task=False,
      output_uri='s3://nathan-internship/clearml-artifacts',
      auto_connect_arg_parser=True,
      auto_connect_frameworks=True,
      auto_resource_monitoring=True,
      auto_connect_streams=True,    
    )



parser = argparse.ArgumentParser()

parser.add_argument('verse_split', metavar='V', type=bool, nargs=1,
                            help='If set to false, split chapter by sentence, not verse.')


args = parser.parse_args()

# a place to import chapter text files in their original language if available
if not os.path.exists('og_script'):
    os.makedirs('og_script')

try:
    og = Dataset.get(dataset_project='IDX_Nathan_Internship',
                                    dataset_name='original script data')
    og.get_mutable_local_copy(target_folder='og_script')
except:
    pass

# a place to import chapter text files
if not os.path.exists('mfa_input'):
    os.makedirs('mfa_input')

mfa = Dataset.get(dataset_project='IDX_Nathan_Internship',
                                  dataset_name='preprocessing data')
mfa.get_mutable_local_copy(target_folder='mfa_input')

# a place for mfa text grids to go
if not os.path.exists('grids'):
    os.makedirs('grids')

grids = Dataset.get(dataset_project='IDX_Nathan_Internship', dataset_name='mfa data')
grids.get_mutable_local_copy(target_folder='grids')

def get_data(name, verse_split=True):
    # Returns 2 lists. One with verse reference and text and one with verse reference and word list 
    phrase_no = 1

    if len(os.listdir('og_script')) == 0:
        with open('mfa_input/{}.txt'.format(name), 'r') as ver:
            verses = ver.read()
            verses = verses.splitlines()
    else:
        with open('og_script/{}.txt'.format(name), 'r') as ver:
            verses = ver.read()
            verses = verses.splitlines()    

    tok = utokenize.Tokenizer(lang_code='yor')

        # (GEN 1:1, text)
    ref_phrase = []
        # (GEN 1:1, [word57, word1, word32, word5...])
    ref_words = []

    # this loop creates tuples that contain the file name and the tokens of the verse or sentence
    for verse in verses:
        if '<range>' in verse:
            pass
        else:
            if verse_split == True:
                clean_string = re.sub(r'[—….\‘\’,\'-@"“”!\[\]]+', '', verse)
                ref_phrase.append(tuple(('{name}_file_{phrase_no}'.format(name=name, phrase_no=phrase_no), clean_string)))
                tokens = tok.utokenize_string(clean_string.lower())
                ref_words.append(tuple(('{name}_file_{phrase_no}'.format(name=name, phrase_no=phrase_no), tokens.split())))
                phrase_no = phrase_no + 1
            else:   
                sentences = verse.split('.')

                for sentence in sentences:
                    clean_string = re.sub(r'[—….\‘\’,\'-@"“”!\[\]]+', '', sentence)
                    if len(clean_string) > 0:
                        ref_phrase.append(
                            tuple(('{name}_file_{phrase_no}'.format(name=name, phrase_no=phrase_no), clean_string)))

                        tokens = tok.utokenize_string(clean_string.lower())
                        ref_words.append(tuple(('{name}_file_{phrase_no}'.format(name=name, phrase_no=phrase_no), tokens.split())))
                        phrase_no = phrase_no + 1

    ref_phrase.pop()
    ref_words.pop()

    return ref_phrase, ref_words


if not os.path.exists('aud_frags'):
    os.makedirs('aud_frags')

for file in os.listdir('grids'):
    
    grid = textgrids.TextGrid('grids/{}'.format(file))
    data = grid['words']

    
    # [(word, start_time, end_time), ...]
    word_time = []

    for i in data:
        if len(i.text) >= 1:
            clean_string = re.sub(r'[—….\‘\’,\'-@"“”!\[\]]+', '', i.text)
            word_time.append(tuple((clean_string, i.xmin, i.xmax)))


    matching_txt = file.replace('.TextGrid', '')
    ref_phrase, ref_words = get_data(name=matching_txt, verse_split=args.verse_split[0])


    audio = AudioSegment.from_wav('mfa_input/{}.wav'.format(matching_txt))

    for phrase in range(len(ref_phrase)):
        first_word = ref_words[phrase][1][0]
        previous_word = ref_words[phrase-1][1][-1]
        
        phrase_length = len(ref_phrase[phrase][1].split())

        if phrase == 0:
            start_time = int(word_time[0][1] * 1000)
            end_time = int(word_time[phrase_length - 1][2] * 1000)
            with open('timestamps.txt', 'a') as f:
                f.write('{chapter}_file_{phrase_no}......{start_time}\n'.format(chapter=matching_txt, phrase_no=phrase + 1, start_time=start_time))
            new_audio = audio[start_time:end_time]
            new_audio.export('aud_frags/{chapter}_file_{phrase_no}.wav'.format(chapter=matching_txt, phrase_no=phrase + 1),
                                format='wav')

            with open('metadata.csv', 'a') as meta:
                meta.write('{chapter}_file_{phrase_no}|{phrase_txt}|{phrase_txt},\n'.format(chapter=matching_txt, phrase_no=phrase + 1, phrase_txt=ref_phrase[phrase][1]))

        # look for start and end times
        else:
            for word in range(len(word_time)):
                if first_word == word_time[word][0] and previous_word == word_time[word-1][0]:
                    original_verse = ref_words[phrase][1]
                    potential_match = word_time[word:word+(phrase_length)]
                    potential_match = [word[0] for word in potential_match]
                    
                    if original_verse == potential_match:
                        start_time = int(word_time[word - 1][2] * 1000)
                        end_time = int(word_time[word + phrase_length - 1][2] * 1000)
                        with open('timestamps.txt', 'a') as f:
                            f.write('{chapter}_file_{phrase_no}......{start_time}\n'.format(chapter=matching_txt, phrase_no=phrase + 1, start_time=start_time))
                        new_audio = audio[start_time:end_time]
                        new_audio.export('aud_frags/{chapter}_file_{sent_no}.wav'.format(chapter=matching_txt, sent_no=phrase + 1),
                                            format='wav')
            
                        with open('metadata.csv', 'a') as meta:
                            line = '{chapter}_file_{sent_no}|{phrase_txt}|{phrase_txt},\n'.format(chapter=matching_txt, sent_no=phrase + 1, phrase_txt=ref_phrase[phrase][1])
                            meta.write(line)

with open('metadata.csv', 'r+') as meta:
    lines = meta.readlines()
    lines.pop()
    for line in lines:
        meta.write(line)

df = pd.read_csv('metadata.csv')
df.drop_duplicates(subset=None, inplace=True)
df.to_csv('clean_metadata.csv', index=False, header=False)

dataset = Dataset.create(dataset_name='mfa to coqui data', 
                          dataset_project='IDX_Nathan_Internship',
                          output_uri='s3://nathan-internship/clearml-artifacts')
dataset.add_files('clean_metadata.csv')
dataset.upload()
dataset.add_files('aud_frags')
dataset.upload()
dataset.finalize()

task.upload_artifact('timings', artifact_object='timestamps.txt')
