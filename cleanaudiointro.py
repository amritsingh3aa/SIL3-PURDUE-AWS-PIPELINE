from pydub import AudioSegment, silence
import os

class IntroCleaner:
    def __init__(self, audio, n_split):
        self.audio = audio # path to audio files to clean
        self.n = n_split # how many chunks do you want to git rid of?

    def remove(self):
        for (path, folder, sound) in os.walk(self.audio):
            for file in sound:
                file_name = '{}'.format(file)
                no_ext = file_name.split('.')
                name = no_ext[0] + '.wav'
                audio = AudioSegment.from_wav(f'{path}/{name}')
                sil = silence.detect_silence(audio, min_silence_len=1000, silence_thresh=-32)
                sil = [((start), (stop)) for start, stop in sil]
                cleaned_audio = audio[sil[self.n][1] - 500:]
                cleaned_audio.export(f'mfa_data/{name}', format='wav')
                print('Cleaned {}.'.format(name))


print('Cleaning audio intros.')
clean = IntroCleaner(audio='clean_background',n_split=1)
clean.remove()

print('Finished audio cleaning.')

print('Cleaning audio intros.')
clean = IntroCleaner(audio='raw_audio', n_split=1)
clean.remove()
