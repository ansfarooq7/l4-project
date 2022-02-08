# Prototypes

* Text-generation with rhyme and rhythm
* Ans Farooq
* 2390370f
* Jake Lever

## Intro

* This file contains information and reflections about each prototype of the project.

## 29/10/2021 - First Prototype - _L4_Project_first.ipynb_

### Current state/Improvements made
* The first prototype combines a causal language model and a masked language model, GPT-2 and RoBERTa, to generate the starts of sentences and fill in the rest until the end rhyming word. 

* For this prototype, the starting word and end rhyming word of each line was pre-determined and hard-coded. This was temporary as I was focused on getting GPT-2 and RoBERTa working and generating some coherent lines of text.

### Future improvements

* Use a Python library to generate rhyming words
* Use user input for the topic of the limerick
* Feed summary of topic from wikipedia to GPT-2 before it generates the start of each line

## 16/11/2021 - Second Prototype - _L4_Project_second.ipynb_

### Current state
* The second prototype uses GPT-2 and RoBERTA, but instead of hard-coded starting and end rhyming words, it uses the *pronouncing* Python library to find rhyming words and the *wikipedia* library to feed a summary of the topic to GPT-2 before generation.

### Future improvements
* Word frequencies/counts for filtering rhyming library words
* Generate the first line a few times until a decent end word, e.g noun, hand-built filters, or word list
* Have a look into improving the rhyme finding, better libraries? Phonetics? Could just filter out words with multiple pronunciations.

## 11/01/2022 - Third Prototype - _L4_Project_third.ipynb_

### Current state
* The third prototype uses GPT-2 and RoBERTA, but instead of the *pronouncing* Python library to find rhyming words - it uses NLTK cmudict *(Natural Language Toolkit: Carnegie Mellon Pronouncing Dictionary)*. 
* Further, it repeatedly generates lines until it generates one with a decent end word, and it uses a word frequency list to filter out rare words that wouldn't have good rhymes. 
* Instead of directly using HuggingFace Transformers' GPT-2 pre-trained language model, it uses a Python package called *aitextgen* that has specific optimisations for text generation using GPT-2.

### Future improvements
* Instead of giving the same wikipedia summary of the given topic as a prompt for generating each line, only give it as a prompt for the first line and then use wiki summary and the lines generated so far as the prompt for the following lines.
* Use another language model (GPT-J?) to get some information about the given topic to use as a prompt instead of the wikipedia summaries. Then run a user study comparing these two methods.
* Use HuggingFace Spaces