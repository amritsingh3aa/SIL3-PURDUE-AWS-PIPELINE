import os
import shutil
import wget
from zipfile import ZipFile

class Download:
    def __init__(self, lang, bib) -> None:
        self.lang = lang
        self.bib = bib

    def download(self):
    # list of all possible books
        books = ['MAT', 'MRK', 'LUK', 'JHN', 'ACT', 'ROM', '1CO', '2CO', 'GAL', 'EPH', 'PHP',
                'COL', '1TH', '2TH', '1TI', '2TI', 'TIT', 'PHM', 'HEB', 'JAS', '1PE',
                '2PE', '1JN', '2JN', '3JN', 'JUD', 'REV']

        '''
        old testament: 'GEN', 'EXO', 'LEV', 'NUM', 'DEU', 'JOS', 'JDG', 'RUT', '1SA', '2SA',
        '1KI', '2KI', '1CH', '2CH', 'EZR', 'NEH', 'EST', 'JOB', 'PSA', 'PRO',
        'ECC', 'SNG', 'ISA', 'JER', 'LAM', 'EZK', 'DAN', 'HOS', 'JOL', 'AMO',
        'OBA', 'JON', 'MIC', 'NAM', 'HAB', 'ZEP', 'HAG', 'ZEC', 'MAL',
        '''

        '''
        apocrypha: , 'TOB', 'JDT', 'ESG', 'WIS',
                'SIR', 'BAR', 'LJE', 'S3Y', 'SUS', 'BEL', '1MA', '2MA', '3MA', '4MA',
                '1ES', '2ES', 'MAN', 'PS2', 'ODA', 'PSS', 'EZA', 'JUB', 'ENO'
        '''

        lang_code = self.lang
        bible_version = self.bib

        urls = []

        for book in books:
            urls.append('https://downloads.open.bible/audio/{lang}/{lang}{version}/{lang}{version}_{book}_wav.zip'.format(lang=lang_code, version=bible_version, book=book))

        if not os.path.exists('zip_files'):
            os.makedirs('zip_files')

        if not os.path.exists('raw_audio'):
            os.makedirs('raw_audio')


        for url in urls:
            try:
                files = wget.download(url, out='zip_files')
                print('Downloaded {}'.format(url))
            except:
                print('Could not retrieve {}'.format(url))

        print('Finished downloading all files.')
        print('Extracting files...')

        for (path, folder, sound) in os.walk('zip_files'):
            for file in sound:
                with ZipFile(path + '/' + file, 'r') as zipObj:
                    zipObj.extractall(path='raw_audio')
                    print('Extracted {}.'.format(file))

        print('Finished extracting files.')
        print('Deleting zip files...')

        shutil.rmtree('zip_files')
		
print('Downloading audio data.')
dl = Download(lang='yo', bib='OBYO17')
dl.download()

print('Finished downloading data.')
