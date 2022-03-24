# Readme

The code is all contained within a single IPython Notebook (Jupyter Notebook) named `l4_project.ipynb` which was created and worked on over time in Google Colab.

The first **Imports** section of the notebook contains all the `pip install` and `import` statements for the Python packages required by the code. It also initialises the pre-trained RoBERTa and GPT-2 models and a text-generation pipeline from HuggingFace Transformers.

The second **Helper functions** section of the notebook contains helper functions used later in the code to perform tasks such as filtering out rare words with poor/no rhymes, removing punctuation from text and getting rhymes for a given word.

The third **RoBERTa** section of the notebook contains the function used to fill in the blank words in lines using the RoBERTa model from HuggingFace Transformers.

The fourth **GPT-2 + RoBERTa** section of the notebook contains the fuctions used to generate each line of the limerick, using both the GPT-2 and RoBERTa models.

The fifth **Limerick generation** section of the notebook contains the main logic of the code, handled by the `generate()` and `compare_summaries()` functions.

## Build instructions

### Requirements

* Jupyter Notebook or Google Colab (or test on Gradio app hosted on HuggingFace Spaces)
* Packages: listed in `requirements.txt`
    * transformers 4.17.0
    * torch 1.10.0
    * wikipedia 1.4.0
    * nltk 3.2.5
    * gradio 2.8.13
* wordFrequency.txt

### Build steps

#### Google Colab
* Open the notebook at: https://colab.research.google.com/drive/1FnzTROJ72EbgV73zbhaXrVcX9wT7CY4N?usp=sharing
* Copy to your own drive
* Upload `wordFrequency.txt` from the `\src` folder
* Run all the cells in order

#### Jupyter Notebook
* Open `l4_project.ipynb` in the `\src` folder#
* Ensure `wordFrequency.txt` is in the same folder as `l4_project.ipynb`
* Run all the cells in order

#### HuggingFace Spaces
* Go to: https://huggingface.co/spaces/ansfarooq7/l4-project
* Enter a topic when prompted in the Gradio app and wait for the limericks to be generated

### Test steps

* Run all the cells in order
* Enter a topic when prompted in the Gradio app and wait for the limericks to be generated
