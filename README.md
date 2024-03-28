# COMS 6111 Project 2 - ReadMe

## Team Members
- Ziang Xu (zx2462)
- Dongbing Han (dh3071)

## Submitted Files
- `project2.py`: This file is used for invoking the Google search system, parsing URLs for text, and iteratively extracting tuple relations until the required criteria are met.
- `call_bert.py`: Utilized for extracting tuple relations from sentences using the SpanBERT model.
- `call_gemini.py`: Employed for extracting tuple relations from sentences using the Google Gemini model.

## Internal Design

### `project2.py`
- **GoogleSearchAPI Class**: Defines a class for interacting with the Google Custom Search API, including methods for calling the API, formatting results, fetching and parsing URLs, extracting text from HTML, and processing URLs to extract text.
- **Iterative Extraction Functions**: Defines functions for the iterative extraction of tuple relations (`iterative_extraction` and `iterative_extraction_gemini`). These functions perform searches, extract relations from search results, and generate new queries based on extracted relations until a specified number of tuple relations are obtained.
- **Main Block**: Parses command-line arguments to determine the search type (SpanBERT or Gemini), API keys, and other parameters. Initializes the appropriate relation extractor and search API, and starts the iterative extraction process.

### Gemini Relation Extraction
- Initializes the Gemini relation extraction module, loads the spaCy model, sets up the Gemini API, and defines parameters for the Gemini model.
- **Functionality**:
  - Processes text to extract relations using the Gemini model.
  - Iterates through sentences, extracting candidate entity pairs.
  - Generates prompts specific to the relation type for each sentence and extracts relations using the Gemini model.
  - Filters extracted relations based on the relation type and entity types.

### BertRelationExtraction Class
- Initializes the spaCy model and the SpanBERT model with specified paths and stores the relation entity types.
- **Functionality**:
  - Processes text to extract relations using the SpanBERT model.
  - Iterates through sentences, extracting candidate entity pairs.
  - Predicts relations using SpanBERT for each sentence and stores relations above a specified confidence threshold.

## Required APIs
- Google Custom Search Engine API: `AIzaSyC5v2l8vS4TZEIgsOeyrLXXXXXX`
- Engine ID: `62edd2XXXXX`
- Google Gemini API key: `AIzaSyD9otDl9zplDgPvLkCev0m3QTXXXXXXXX`

## Running Instructions

### Setups
1. Navigate to Ziang's directory: `cd /home/zx2462`
2. Activate the virtual environment: `source dbproj/bin/activate`
3. Navigate to the SpanBERT directory: `cd proj2/SpanBERT`

### Running
- General command: `python3 project2.py [-spanbert|-gemini] <google api key> <google engine id> <google gemini api key> <r> <t> <q> <k>`
- **Running Gemini Example**:
  ```bash
  python3 project2.py -gemini AIzaSyC5v2l8vS4TZEIgsOeXXXXXXXX 62edd23ecdaXXXXXXS yD9otDl9zXXXXXXXg 1 0.7 "sergey brin stanford" 10
  ```
- **Running SpanBert Example**:
  ```bash
  python3 project2.py -spanbert AIzaSyC5v2l8vXXXXXXXX 62eddXXXXXc4041 AIzaSyD9otXXXXXXXX 1 0.7 "sergey brin stanford" 10
  ```

---
