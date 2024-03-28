import google.generativeai as genai
from spacy_help_functions import *

import re

class GeminiRelationExtraction:
    def __init__(self, spacy_model, gemini_api_key, relation_entity_types, relation_id):
        'Defination of Spacy Model: '
        self.nlp = spacy.load(spacy_model)
        self.relation_entity_types = relation_entity_types
        self.relation_id = int(relation_id)

        'Defination of Geimini: '
        # gemini_api_key_list = ["AIzaSyDyeq4E5dNYsQqzXz3X6B_q7kfKUir9pcE", "AIzaSyD9otDl9zplDgPvLkCev0m3QTzZ_UzDUsg", "AIzaSyD9otDl9zplDgPvLkCev0m3QTzZ_UzDUsg"]
        # self.GEMINI_API_KEY = gemini_api_key_list[0]  # Substitute your own key here
        # AIzaSyDyeq4E5dNYsQqzXz3X6B_q7kfKUir9pcE # AIzaSyD9otDl9zplDgPvLkCev0m3QTzZ_UzDUsg # AIzaSyD9otDl9zplDgPvLkCev0m3QTzZ_UzDUsg
        self.gemini_api_key = gemini_api_key
        genai.configure(api_key=self.gemini_api_key)

        'Defination of Geimini Model Parameter: '
        self.model_name = 'gemini-pro'
        self.max_tokens = 100
        self.temperature = 0.2
        self.top_p = 1
        self.top_k = 32

        # print(f"Loaded spaCy model '{spacy_model}' and Gemini model from '{self.model_name}'.")

    def get_entities_of_interest_for_relation(self, relation_id):
        relation = self.relation_entity_types[relation_id]
        entities_of_interest = set([relation["subj"]])
        if isinstance(relation["obj"], list):
            entities_of_interest.update(relation["obj"])
        else:
            entities_of_interest.add(relation["obj"])
        print(f"Entities of interest for relation {relation_id}: {list(entities_of_interest)}")
        return list(entities_of_interest)


    def create_prompt(self, sentence, relation_id):
        # Get the example for the specified relation

        # Define regex pattern to match special characters
        pattern = r'[^\w\s\d.,;:\'"\(\){}\[\]]'
        # Replace special characters with empty string
        normalized_sentence = re.sub(pattern, '', sentence)

        relation_examples = {
            1: '["Jeff Bezos", "Schools_Attended", "Princeton University"]',
            2: '["Alec Radford", "Work_For", "OpenAI"]',
            3: '["Mariah Carey", "Live_In", "New York City"]',
            4: '["Nvidia", "Top_Member_Employees", "Jensen Huang"]',
        }

        if int(relation_id) == 1:
            prompt_text = f"Given the sentence: '{normalized_sentence}', prompt to identify the relationship between the subject and object in the context of 'schools attended'. Provide both the subject which is a person and the object which should be an organization such as university or middle school. Then, request please to return a relationship in format similar to: '{relation_examples[1]}'."
        elif int(relation_id) == 2:
            prompt_text = f"Given the sentence: '{normalized_sentence}', prompt to identify the relationship between the subject and object in the context of 'work for'. Provide both the subject which is a person and the object which should be an organization such as company, lab or non-project organization. Then, request please to return a relationship in format similar to: '{relation_examples[2]}'."
        elif int(relation_id) == 3:
            prompt_text = f"Given the sentence: '{normalized_sentence}', prompt to identify the relationship between the subject and object in the context of 'live in'. Provide both the subject which is a person and the object which should be an place such as location, city, state of province, or country. Then, request please to return a relationship in format similar to: '{relation_examples[3]}'."
        elif int(relation_id) == 4:
            prompt_text = f"Given the sentence: '{normalized_sentence}', prompt to identify the relationship between the object and subject in the context of 'top member employees'. Provide both the object which should be an organization such as company, lab or non-project organization and the subject which is a person. Then, request please to return a relationship in format similar to: '{relation_examples[4]}'."

        # # Craft the prompt
        # if int(relation_id) == 1:
        #     prompt_text = f"Given the sentence: '{sentence}', prompt to identify all the possible relationship between the subject and object in the context of 'schools attended'. Provide both the subject which is a person and the object which should be an organization such as university or middle school. Then, if there are multiple relation paris, please return each pair of relationship in format similar to: '{relation_examples[1]}'."
        # elif int(relation_id) == 2:
        #     prompt_text = f"Given the sentence: '{sentence}', prompt to identify all the possible relationship between the subject and object in the context of 'work for'. Provide both the subject which is a person and the object which should be an organization such as company, lab or non-project organization. Then, if there are multiple relation paris, please return each pair of relationship in format similar to: '{relation_examples[2]}'."
        # elif int(relation_id) == 3:
        #     prompt_text = f"Given the sentence: '{sentence}', prompt to identify all the possible relationship between the subject and object in the context of 'live in'. Provide both the subject which is a person and the object which should be an place such as location, city, state of province, or country. Then, if there are multiple relation paris, please return each pair of relationship in format similar to: '{relation_examples[3]}'."
        # elif int(relation_id) == 4:
        #     prompt_text = f"Given the sentence: '{sentence}', prompt to identify all the possible relationship between the object and subject in the context of 'top member employees'. Provide both the object which should be an organization such as company, lab or non-project organization and the subject which is a person. Then, if there are multiple relation paris, please return each pair of relationship in format similar to: '{relation_examples[4]}'."

        # if int(relation_id) == 1:
        #     prompt_text = f"Given the sentence: '{sentence}', prompt to identify the relationship between the subject and object in the context of 'schools attended'. Provide both the subject which is a person and the object which should be an organization such as university or middle school. Then, please to return all the possible relationships in format similar to: '{relation_examples[1]}'."
        # elif int(relation_id) == 2:
        #     prompt_text = f"Given the sentence: '{sentence}', prompt to identify the possible relationship between the subject and object in the context of 'work for'. Provide both the subject which is a person and the object which should be an organization such as company, lab or non-project organization. Then, please to return all the possible relationships in format similar to: '{relation_examples[2]}'."
        # elif int(relation_id) == 3:
        #     prompt_text = f"Given the sentence: '{sentence}', prompt to identify the possible relationship between the subject and object in the context of 'live in'. Provide both the subject which is a person and the object which should be an place such as location, city, state of province, or country. Then, please to return all the possible relationships in format similar to: '{relation_examples[3]}'."
        # elif int(relation_id) == 4:
        #     prompt_text = f"Given the sentence: '{sentence}', prompt to identify the possible relationship between the object and subject in the context of 'top member employees'. Provide both the object which should be an organization such as company, lab or non-project organization and the subject which is a person. Then, please to return all the possible relationships in format similar to: '{relation_examples[4]}'."

        return prompt_text


        # Generate response to prompt
    def get_gemini_completion(self, prompt, model_name, max_tokens, temperature, top_p, top_k):

        # Initialize a generative model
        model = genai.GenerativeModel(model_name)

        # Configure the model with your desired parameters
        generation_config=genai.types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k
        )

        try:
            # Attempt to generate text using the Google Generative AI library
            response = model.generate_content(prompt, generation_config=generation_config)
            
            # If the response is successful, return the generated text
            return response.text

        except Exception as e:
            # Handle the exception
            print("An error occurred:", e)
            # Optionally, you can return a default value or perform other actions as needed
            return None

    def filter_candidate_pairs_for_relation(self, candidate_pairs, relation_id):
        filtered_pairs = []
        required_types = self.relation_entity_types[self.relation_id]

        for pair in candidate_pairs:
            subj_type = pair["subj"][1]
            obj_type = pair["obj"][1]

            if isinstance(required_types["obj"], list):
                obj_flag = obj_type in required_types["obj"]
            else:
                obj_flag = obj_type == required_types["obj"]

            if subj_type == required_types["subj"] and obj_flag:
                filtered_pairs.append(pair)

        return filtered_pairs

    def process_text_and_extract_relations(self, text, relation_id):
        print("\nProcessing text for relation extraction...")

        doc = self.nlp(text)
        entities_of_interest = self.get_entities_of_interest_for_relation(relation_id)
        top_entities = {}
        extracted_relations = set()

        print("Extracting candidate pairs from each sentence...")
        sentence_counter = 0
        for sentence in doc.sents:
            sentence_counter += 1
            if sentence_counter % 5 == 0:
                print(f"Processed {sentence_counter} / {len(list(doc.sents))} sentences")

            # Print the tokenized sentence once for context before listing any relations extracted from it
            tokenized_sentence = "Tokenized sentence: {}".format([token.text for token in sentence])

            # Using create_entity_pairs for each sentence
            candidate_pairs = []
            sentence_entity_pairs = create_entity_pairs(sentence, entities_of_interest)
            for ep in sentence_entity_pairs:
            # TODO: keep subject-object pairs of the right type for the target relation (e.g., Person:Organization for the "Work_For" relation)
                candidate_pairs.append({"tokens": ep[0], "subj": ep[1], "obj": ep[2]})
                candidate_pairs.append({"tokens": ep[0], "subj": ep[2], "obj": ep[1]})

            candidate_pairs = [p for p in candidate_pairs if not p["subj"][1] in ["DATE", "LOCATION"]]
            filtered_pairs = self.filter_candidate_pairs_for_relation(candidate_pairs, relation_id)

            if filtered_pairs:
                # print("Predicting relations using SpanBERT for the current sentence..."
                print("\nSend to Gemini:")
                sentence = str(sentence)
                prompt_text = self.create_prompt(sentence, relation_id)
                #print("Sentence Send: ", sentence)
                print("Prompt Text: ", prompt_text)
                relation_preds = self.get_gemini_completion(prompt_text, self.model_name, self.max_tokens, self.temperature, self.top_p, self.top_k)
                #print("Relation Predicted: ", relation_preds, " Types: ", type(relation_preds))
                try:
                    # Find all pairs within the Relationship section
                    start_index = relation_preds.find("[")
                    while start_index != -1:
                        end_index = relation_preds.find("]", start_index)
                        if end_index != -1:
                            # Extract the Relationship section
                            relationship_section = relation_preds[start_index:end_index + 1].strip()

                            # Remove leading and trailing whitespace and extract the relation
                            relation_pair = relationship_section.strip('][').split(', ')
                            relation_pair = [part.strip('"') for part in relation_pair]
                            # Convert string to list
                            relation_pair_list = [element.strip(' "[]') for element in relation_pair]
                            #print("\nInitial Check Pairs List:", relation_pair_list)

                            # Check the relationship type based on the relation ID
                            if relation_id == 1 and relation_pair[1] == "Schools_Attended":
                                print("Extracted Relation Pair Type 1:", relation_pair, type(relation_pair))
                                extracted_relations.add(tuple(relation_pair))
                            elif relation_id == 2 and relation_pair[1] == "Work_For":
                                print("Extracted Relation Pair Type 2:", relation_pair, type(relation_pair))
                                extracted_relations.add(tuple(relation_pair))
                            elif relation_id == 3 and relation_pair[1] == "Live_In":
                                print("Extracted Relation Pair Type 3:", relation_pair, type(relation_pair))
                                extracted_relations.add(tuple(relation_pair))
                            elif relation_id == 4 and relation_pair[1] == "Top_Member_Employees":
                                print("Extracted Relation Pair Type 4:", relation_pair, type(relation_pair))
                                extracted_relations.add(tuple(relation_pair))
                            else:
                                print("Relation ID does not match or relationship type not found.")

                            # Find the next pair
                            start_index = relation_preds.find("[", end_index)
                        else:
                            print("Could not find a closing bracket for a pair.")
                            break
                except Exception as e:
                    print(f"An error occurred while extracting the relationship: {e}")

        print(f"\nTotal processed sentences: {sentence_counter}")
        print(f"\nNumber of Extracted Relations: {len(extracted_relations)}, Final Extracted Relations Pairs: {extracted_relations}")
        return list(extracted_relations)