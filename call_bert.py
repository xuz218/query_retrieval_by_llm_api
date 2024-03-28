import spacy
from spanbert import SpanBERT
from spacy_help_functions import get_entities, create_entity_pairs
class BertRelationExtraction:
    def __init__(self, spacy_model, spanbert_model_path, relation_entity_types, confidence_threshold):
        self.nlp = spacy.load(spacy_model)
        self.spanbert = SpanBERT(spanbert_model_path)
        self.relation_entity_types = relation_entity_types
        self.confidence_threshold = float(confidence_threshold)
        print(f"Loaded spaCy model '{spacy_model}' and SpanBERT model from '{spanbert_model_path}'.")

    def get_entities_of_interest_for_relation(self, relation_id):
        relation = self.relation_entity_types[relation_id]
        entities_of_interest = set([relation["subj"]])
        if isinstance(relation["obj"], list):
            entities_of_interest.update(relation["obj"])
        else:
            entities_of_interest.add(relation["obj"])
        print(f"Entities of interest for relation {relation_id}: {list(entities_of_interest)}")
        return list(entities_of_interest)

    def process_text_and_extract_relations(self, text, relation_id):
        print("\nProcessing text for relation extraction...")
        doc = self.nlp(text)
        entities_of_interest = self.get_entities_of_interest_for_relation(relation_id)
        top_entities = {}
        extracted_relations = []
        relation_names = {
            1: ["per:schools_attended"],
            2: ["per:employee_of"],
            3: ["per:countries_of_residence", "per:stateorprovinces_of_residence", "per:cities_of_residence"],
            4: ["org:top_members/employees"]
        }

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
                # print("Predicting relations using SpanBERT for the current sentence...")
                relation_preds = self.spanbert.predict(filtered_pairs)

                for ex, pred in zip(filtered_pairs, relation_preds):
                    if pred[1] >= self.confidence_threshold and pred[0] in relation_names[relation_id]:
                        print(f"=== Extracted Relation ===")
                        print(str(sentence))
                        print(f"\tSubject: {ex['subj'][0]}, Object: {ex['obj'][0]}, Relation: {pred[0]}, Confidence: {pred[1]:.5f}")
                        entity_pair = (ex["subj"][0], ex["obj"][0])
                        if entity_pair not in top_entities or pred[1] > top_entities[entity_pair][1]:
                            top_entities[entity_pair] = (pred[0], pred[1])
                            extracted_relations.append({"subject": ex["subj"][0], "object": ex["obj"][0], "relation": pred[0], "confidence": pred[1]})

        print(f"\nTotal processed sentences: {sentence_counter}")
        return extracted_relations

    def filter_candidate_pairs_for_relation(self, candidate_pairs, relation_id):
        filtered_pairs = []
        required_types = self.relation_entity_types[relation_id]

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