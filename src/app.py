from transformers import RobertaTokenizer, RobertaForMaskedLM, GPT2Tokenizer, GPT2LMHeadModel, pipeline
import torch
import wikipedia
import re
import random
import nltk
import gradio as gr
nltk.download('cmudict')

roberta_tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
roberta_model = RobertaForMaskedLM.from_pretrained('roberta-base')

gpt2_tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
gpt2_model = GPT2LMHeadModel.from_pretrained("gpt2", pad_token_id=gpt2_tokenizer.eos_token_id)

gpt2_pipeline = pipeline('text-generation', model=gpt2_model, tokenizer=gpt2_tokenizer)

frequent_words = set()
        
with open("wordFrequency.txt", 'r') as f:
    line = f.readline()
    while line != '':  # The EOF char is an empty string
        frequent_words.add(line.strip())
        line = f.readline()

def filter_rhymes(word):
    filter_list = ['an', 'to', 'on', 'has', 'but', 'the', 'in', 'and', 'a', 'are', 'or', 'its', 'it''s'] 
    if word in filter_list:
        return False
    else:
        return True

def remove_punctuation(text):
    text = re.sub(r'[^\w\s]', '', text)
    text = text.replace("\n", " ")
    return text.strip()

def get_rhymes(inp, level):
    entries = nltk.corpus.cmudict.entries()
    syllables = [(word, syl) for word, syl in entries if word == inp]
    rhymes = []
    filtered_rhymes = set()
    for (word, syllable) in syllables:
        rhymes += [word for word, pron in entries if pron[-level:] == syllable[-level:]]
    
    for word in rhymes:
        if (word in frequent_words) and (word != inp):
            filtered_rhymes.add(word)
    return filtered_rhymes

def get_inputs_length(input):
    input_ids = gpt2_tokenizer(input)['input_ids']
    return len(input_ids)
    
def get_prediction(sent):
    token_ids = roberta_tokenizer.encode(sent, return_tensors='pt')
    masked_position = (token_ids.squeeze() == roberta_tokenizer.mask_token_id).nonzero()
    masked_pos = [mask.item() for mask in masked_position ]

    with torch.no_grad():
        output = roberta_model(token_ids)

    last_hidden_state = output[0].squeeze()

    list_of_list =[]
    for index,mask_index in enumerate(masked_pos):
        words = []
        while not words:
            mask_hidden_state = last_hidden_state[mask_index]
            idx = torch.topk(mask_hidden_state, k=5, dim=0)[1]
            for i in idx:
                word = roberta_tokenizer.decode(i.item()).strip()
                if (remove_punctuation(word) != "") and (word != '</s>'):
                    words.append(word)
        list_of_list.append(words)
        print(f"Mask {index+1} Guesses: {words}")
    
    best_guess = ""
    for j in list_of_list:
        best_guess = best_guess+" "+j[0]
        
    return best_guess
    
def get_line(prompt, inputs_len):
    output = gpt2_pipeline(
        prompt + ".",
        min_length=4,
        max_length=inputs_len + 7,
        clean_up_tokenization_spaces=True,
        return_full_text=False
    )
    return remove_punctuation(output[0]['generated_text'])

def get_rhyming_line(prompt, rhyming_word, inputs_len):
    output = gpt2_pipeline(
        prompt + ".",
        min_length=4,
        max_length=inputs_len + 3,
        clean_up_tokenization_spaces=True,
        return_full_text=False
    )
    gpt2_sentence = remove_punctuation(output[0]['generated_text'])
    while len(gpt2_sentence) == 0:
        output = gpt2_pipeline(
            prompt + ".",
            min_length=4,
            max_length=inputs_len + 3,
            clean_up_tokenization_spaces=True,
            return_full_text=False
        )
        gpt2_sentence = remove_punctuation(output[0]['generated_text'])
    
    print(f"\nGetting rhyming line starting with '{gpt2_sentence}' and ending with rhyming word '{rhyming_word}'")
    sentence = gpt2_sentence + " ___ ___ ___ " + rhyming_word
    print(f"Original Sentence: {sentence}")
    if sentence[-1] != ".":
        sentence = sentence.replace("___","<mask>") + "."
    else:
        sentence = sentence.replace("___","<mask>")
    print(f"Original Sentence replaced with mask: {sentence}")
    print("\n")
 
    predicted_blanks = get_prediction(sentence)
    print(f"\nBest guess for fill in the blanks: {predicted_blanks}")
    final_sentence = gpt2_sentence + predicted_blanks + " " + rhyming_word
    print(f"Final Sentence: {final_sentence}")
    return final_sentence

def gpt2_summary(topic):
    output = gpt2_pipeline(
        f"Here is some information about {topic}.",
        min_length=100,
        max_length=300,
        clean_up_tokenization_spaces=True,
        return_full_text=False
    )
    return remove_punctuation(output[0]['generated_text'])
    
def generate(topic, wiki=True):
    if wiki:
        try:
            topic_search = wikipedia.search(topic, results=3)
            print(f"Wikipedia search results for {topic} are: {topic_search}")
            topic_summary = remove_punctuation(wikipedia.summary(topic_search[0], auto_suggest=False))
        except wikipedia.DisambiguationError as e:
            print(f"Wikipedia returned a disambiguation error for {topic}. Selecting the first option {e.options[0]} instead.")
            page = e.options[0]
            topic_summary = remove_punctuation(wikipedia.summary(page, auto_suggest=False))
        except:
            return(f"Method A struggled to find information about {topic}, please try a different topic!")
    else:
        topic_summary = remove_punctuation(gpt2_summary(topic))

    word_list = topic_summary.split()
    topic_summary_len = len(topic_summary)
    no_of_words = len(word_list)
    inputs_len = get_inputs_length(topic_summary)
    print(f"Topic Summary: {topic_summary}")
    print(f"Topic Summary Length: {topic_summary_len}")
    print(f"No of Words in Summary: {no_of_words}")
    print(f"Length of Input IDs: {inputs_len}")         

    rhyming_words_125 = []
    while len(rhyming_words_125) < 3 or valid_rhyme == False or len(first_line) == 0:
        first_line = get_line(topic_summary, inputs_len)
        if first_line:
            end_word = remove_punctuation(first_line.split()[-1])
            valid_rhyme = filter_rhymes(end_word)
            if valid_rhyme:
                print(f"\nFirst Line: {first_line}")
                rhyming_words_125 = list(get_rhymes(end_word, 3))
                print(f"Rhyming words for '{end_word}' are {rhyming_words_125}")
                limerick = first_line + "\n"

    rhyming_word = random.choice(rhyming_words_125)
    rhyming_words_125.remove(rhyming_word)
    prompt = topic_summary + " " + first_line
    inputs_len = get_inputs_length(prompt)
    print(f"Prompt: {prompt}")
    print(f"Length of prompt: {inputs_len}")
    second_line = get_rhyming_line(prompt, rhyming_word, inputs_len)
    print(f"\nSecond Line: {second_line}")
    limerick += second_line + "\n"

    rhyming_words_34 = []
    prompt = prompt + " " + second_line
    inputs_len = get_inputs_length(prompt)
    print(f"Prompt: {prompt}")
    print(f"Length of prompt: {inputs_len}")
    while len(rhyming_words_34) < 2 or valid_rhyme == False or len(third_line) == 0:
        third_line = get_line(prompt, inputs_len)
        if third_line:
            print(f"\nThird Line: {third_line}")
            end_word = remove_punctuation(third_line.split()[-1])
            valid_rhyme = filter_rhymes(end_word)
            print(f"Does '{end_word}' have valid rhymes: {valid_rhyme}")
            rhyming_words_34 = list(get_rhymes(end_word, 3))
            print(f"Rhyming words for '{end_word}' are {rhyming_words_34}")
            if valid_rhyme and len(rhyming_words_34) > 1:
                limerick += third_line + "\n"

    rhyming_word = random.choice(rhyming_words_34)
    rhyming_words_34.remove(rhyming_word)
    prompt = prompt + " " + third_line
    inputs_len = get_inputs_length(prompt)
    print(f"Prompt: {prompt}")
    print(f"Length of prompt: {inputs_len}")
    fourth_line = get_rhyming_line(prompt, rhyming_word, inputs_len)
    print(f"\nFourth Line: {fourth_line}")
    limerick += fourth_line + "\n"

    rhyming_word = random.choice(rhyming_words_125)
    rhyming_words_125.remove(rhyming_word)
    prompt = prompt + " " + fourth_line
    inputs_len = get_inputs_length(prompt)
    print(f"Prompt: {prompt}")
    print(f"Length of prompt: {inputs_len}")
    fifth_line = get_rhyming_line(prompt, rhyming_word, inputs_len)
    print(f"\nFifth Line: {fifth_line}")
    limerick += fifth_line + "\n"

    print("\n")
    print(limerick)

    return limerick
    
def compare_summaries(topic):
    wiki_limerick = generate(topic)
    gpt2_limerick = generate(topic, wiki=False)

    output1 = wiki_limerick
    output2 = gpt2_limerick
    print(output1 + "\n" + output2)

    return output1, output2
    
description = "Generates limericks (five-line poems with a rhyme scheme of AABBA) using two different methods, please be patient as it can take up to a minute to generate both limericks. You may have to generate multiple times or try different topics in order to produce something of good quality."
article = '<center><big><strong>Limerick Generation</strong></big></center>'\
        '<center><strong>By Ans Farooq</strong></center>'\
        '<center><small>Level 4 Individual Project</small></center>'\
        '<center><small>BSc Computing Science</small></center>'\
        '<center><small>University of Glasgow</small></center>'\
        '<strong>Description</strong><br>'\
        'Recent advances in natural language processing (NLP) have shown '\
        'incredible promise at generating human-quality language. Poetry '\
        'presents an additional challenge as it often relies on rhyme and '\
        'rhythm of language. Factoring these in presents an interesting '\
        'challenge to new deep learning-based methods. This text-generation '\
        'project examines the use of transformer-based deep learning methods '\
        'and the addition of constraints for length, rhyme and rhythm given '\
        'example words to seed a poem. This interface allows you to produce two '\
        'cohesive limericks automatically, using two different methods. The '\
        'results of this project are to be evaluated through human comparisons.'

gr_input = gr.inputs.Textbox(label='Topic')
gr_output1 = gr.outputs.Textbox(label='Method A')
gr_output2 = gr.outputs.Textbox(label='Method B')

interface = gr.Interface(
    fn=compare_summaries, 
    inputs=gr_input, 
    outputs=[gr_output1, gr_output2],
    title="Text-generation with rhyme and rhythm",
    layout="horizontal",
    theme="peach",
    description=description,
    article=article)
interface.launch(debug=True)