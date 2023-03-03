from utoken import utokenize
import re

class MFADict:
    def __init__(self, ver_file, iso, alpha):
        self.file = ver_file # file with language data
        self.code = iso # 3 letter language code
        self.abc = alpha # Is the alphabet Latin "Latn", Cyrillic "Cyrl", Perso-Arabic "Arab", Devanagari "Deva", Chinese "Hans"?

    def dict_gen(self):

        tok = utokenize.Tokenizer(lang_code=self.code)

        with open(self.file, 'r') as file:
            text = file.read()
            lines = text.splitlines()

        # list comprehension to drop any '<range>' values if present
        lines = [line for line in lines if '<range>' not in line]

        # list of all space seperated tokens and strip any punctuation
        words = []
        for verse in lines:
            toks = tok.utokenize_string(verse)

            for i in toks.split():
                # eliminate commas, periods, etc. that are attached to words
                clean_string = re.sub(r'[—…. \‘\’,\'-@"“”!\[\]]+', '', i)
                # ignore empty strings
                if len(clean_string) >= 1:
                    words.append(clean_string.lower())

        tok_set = set(words)

        tok_unique_list = (list(tok_set))

        tok_unique_list.sort() # alphabetized list of unique words

        dict_list = []

        for token in tok_unique_list:
            dict_list.append(f'{token}\t{" ".join(token)}')


        with open("mfa_dict.txt", "w", encoding="utf-8") as file:
            for line in dict_list:
                file.write(f"{line}\n")

mfa_dict = MFADict(ver_file='yor-yor.txt', iso='yor',alpha='Latn')
mfa_dict.dict_gen()
