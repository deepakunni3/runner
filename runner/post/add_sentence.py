from sys import path
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import os
from glob import glob
import nltk

from pandas.core.arrays.categorical import contains
def find_extensions(dr, ext):
    return glob(os.path.join(dr, "*.{}".format(ext)))

def sentencify(input_df, output_df, output_fn):
        '''
        Add relevant sentences to the tokenized term in every row of a pandas DataFrame
        :param df: (DataFrame) pandas DataFrame.
        :return: None
        '''
        
        for j, row in input_df.iterrows():
            idx = row.id
            text = row.text
            # Check for text = NaN
            if text == text:
                text_tok = nltk.sent_tokenize(text)
                sub_df = output_df[output_df['DOCUMENT ID'] == idx]

                if len(text_tok) == 1:
                    sub_df['SENTENCE'] = text
                else:
                    relevant_tok = []
                    start_reached = False
                    end_reached = False
                    for i, row2 in sub_df.iterrows():
                        term_of_interest = row2['MATCHED TERM']
                        start_pos = int(row2['START POSITION'])
                        if start_pos == 0: start_reached = True
                        end_pos = int(row2['END POSITION'])
                        if end_pos == len(text): end_reached = True
                        relevant_tok = [x for x in text_tok if term_of_interest in x]
                        single_tok = relevant_tok
                        count = 0

                        while len(single_tok) != 1:
                            count += 1 # This keeps track of the # of times the start_pos and/or end_pos are shifted

                            # Detect the beginning and ending of sentences ---------------------
                            for tok in single_tok:
                                if tok.startswith(text[start_pos:end_pos]):
                                    start_reached = True
                                        
                            if not start_reached:
                                start_pos -= 1

                            for tok in single_tok:
                                if tok.endswith(text[start_pos:end_pos]):
                                    end_reached = True

                            if not end_reached:
                                end_pos += 1
                            # -------------------------------------------------------------------

                            term_of_interest = text[start_pos:end_pos]
                            
                            
                            single_tok = [x for x in relevant_tok if term_of_interest.strip() in x]

                            if count > 30 and 1 < len(single_tok):
                                single_tok = [single_tok[0]]
                                count = 0
                                break 
                            # Reason for the break:
                            # In some instance the sentences are repeated. In such cases the expanding window
                            # with start_pos and exd_pos goes expanding after 30 character match (arbitrarily)
                            # we take the first element out of the common terms and take that as the SENTENCE
                            # and then 'break'-ing out of the 'while' loop. Else, it'll continue looing for 
                            # the unique sentence forever.
                            # It's a hack but for now it'll do until severe consequences detected.
                            
                            
                            
                        sub_df.loc[i,'SENTENCE'] = single_tok[0]
                        
                        
                if not sub_df.empty:
                    sub_df.to_csv(output_fn, mode='a', sep='\t', header=None, index=None )


def parse(input_directory, output_directory) -> None:
    '''
    This parses the OGER output and adds sentences of relevant tokenized terms for context to the reviewer.
    :param input_directory: (str) Input directory path.
    :param output_directory: (str) Output directory path.
    :return: None.
    '''
    # Get a list of potential input files for particular formats
    input_list_tsv = find_extensions(input_directory, 'tsv')
    input_list_txt = find_extensions(input_directory, 'txt')
    output_files = find_extensions(output_directory, 'tsv')
    output_file = [x for x in output_files if '_node' not in x if '_edge' not in x if 'runNER' not in x][0]
    output_df = pd.read_csv(output_file, sep='\t', low_memory=False)
    output_df['SENTENCE'] = ''

    final_output_file = os.path.join(output_directory, 'runNER_Output.tsv')
    
    pd.DataFrame(output_df.columns).T.to_csv(final_output_file, sep='\t', index=None, header=None)
    
    if len(input_list_tsv) > 0:
        input_df = pd.read_csv(input_list_tsv[0], sep='\t', low_memory=False, index_col=None)
        sentencify(input_df, output_df, final_output_file)

    if len(input_list_txt) > 0:
        # Read each text file such that Id = filename and text = full text
        import pdb; pdb.set_trace()
        pass

    '''for row in input_df.iterrows():
        idx = row[1].Id
        text = row[1].Text


        text_tok = out_tok = nltk.sent_tokenize(text)

        sub_df = output_df[output_df['DOCUMENT ID'] == idx]

        if len(text_tok) == 1:
            sub_df['SENTENCE'] = text
        else:
            sent_row = []
            relevant_tok = []
            for i, row2 in sub_df.iterrows():
                term_of_interest = row2['MATCHED TERM']
                start_pos = int(row2['START POSITION'])
                end_pos = int(row2['END POSITION'])
                while len(relevant_tok) != 1:
                    relevant_tok = [x for x in text_tok if term_of_interest in x]
                    text_tok = relevant_tok
                    if start_pos != 0:
                        start_pos -= 1
                    if end_pos != len(text):
                        end_pos += 1
                    term_of_interest = text[start_pos:end_pos]
                    

                sub_df.at[i,'SENTENCE'] = relevant_tok[0]
                import pdb; pdb.set_trace()
        
        if not sub_df.empty:
            sub_df.to_csv(final_output_file, mode='a', sep='\t', header=None, index=None )'''


    