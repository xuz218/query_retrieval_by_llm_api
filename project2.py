import sys
import requests
from bs4 import BeautifulSoup
import spacy
import random
from call_bert import BertRelationExtraction
from call_gemini import GeminiRelationExtraction

class GoogleSearchAPI:
    def __init__(self, search_type, api_key, engine_id, gemini_api_key, relation_id, confidence, query, tuple_num):
        self.search_type = search_type
        self.api_key = api_key # "AIzaSyC5v2l8vS4TZEIgsOeyrLUeBATHkmKBf58"
        self.engine_id = engine_id # "62edd23ecda9c4041"
        self.gemini_api_key = gemini_api_key # "AIzaSyD9otDl9zplDgPvLkCev0m3QTzZ_UzDUsg"
        self.relation_id = int(relation_id)
        self.confidence = float(confidence)
        self.query = query
        self.tuple_num = int(tuple_num)


    def call_google_api(self):
        """
        Retrieve information from google search engine.

        :param api_key, engine_id, query
        :return results: the original results from google search
        """
        # print(f"API Key: '{self.api_key}'")
        # print(f"API Key: '{self.engine_id}'")

        url = f"https://www.googleapis.com/customsearch/v1?key={self.api_key}&cx={self.engine_id}&q={self.query}"
        response = requests.get(url)
        results = response.json()
        return results

    def getFormattedData(self, results):
        """
        Formatted the retrieved information and split into title, link, snippet.

        :param results : the original results from google search
        :return formatted_results :  list of dictionaries containing unlabeled search results and separated by links.
        """
        formatted_results = {"items": []}
        for item in results["items"]:
            formatted_result = {
                # "title": item["title"],
                "link": item["link"],
                # "snippet": item["snippet"]
            }
            formatted_results["items"].append(formatted_result)
        return formatted_results

    def fetch_and_parse(self, url):
        """
        Extract information by requesting the url link.

        :param url: URL to fetch data from
        :return: text from the URL, or None if an error occurs
        """
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print("Success")
                return response.text
            else:
                print(f"Error: Status code {response.status_code} for {url}")
        except requests.Timeout:
            print(f"Timeout occurred for {url}")
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
        return None

    def extract_text(self, html):
        """
        Extract information by BeautifulSoup within a given url

        :param html :
        :return text: text in that html_content
        """
        soup = BeautifulSoup(html, 'html.parser')
        for script in soup(["script", "style"]):
          script.decompose()
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        return text


    def process_urls(self, urls):
        """
        Process and grasping text by retrevied urls

        :param results : urls after google search
        :return text: the plain text of information in urls
        """
        texts = []
        for url in urls['items']:
            html_content = self.fetch_and_parse(url['link'])
            if html_content:
                cur_text = self.extract_text(html_content)
                if len(cur_text) > 10000:
                    cur_text = cur_text[:10000]
                print(f"Processed text from {url}")
                texts.append(cur_text)
        return texts

    def process_and_extract_relations(self, relation_extractor, relation_id, confidence):
        print("Calling Google API...")
        results = self.call_google_api()
        print("Formatting results...")
        formatted_results = self.getFormattedData(results)
        print("Processing URLs to extract text...")
        texts = self.process_urls(formatted_results)

        all_extracted_relations = []
        for text in texts:
            if len(text)<=40:
                continue
            print("\n=+=+=+=+=+= Extracting Relations From Text of New Url =+=+=+=+=")
            extracted_relations = relation_extractor.process_text_and_extract_relations(text, relation_id)
            all_extracted_relations.extend(extracted_relations)

        return all_extracted_relations

def iterative_extraction(search_api, relation_extractor, initial_query, queries_used, all_extraction, tuple_num):
    queries_used.add(initial_query)
    current_query = initial_query
    iter = 0

    unique_subject_object_pairs = { (relation['subject'], relation['object']): relation for relation in all_extraction }
    while len(all_extraction) < tuple_num:
        print(f"================ Iteration {iter}:Current Query Processing: {current_query} ======================")
        iter+=1

        # Update search_api with the current query
        search_api.query = current_query
        extracted_relations = search_api.process_and_extract_relations(relation_extractor, search_api.relation_id, search_api.confidence)

        if not extracted_relations:
            print("No new tuples extracted. Not enough k tuples found.")
            return

        # Sort extracted relations by confidence, descending
        extracted_relations.sort(key=lambda x: x['confidence'], reverse=True)

        # Extend the all_extraction with newly extracted relations
        for relation in extracted_relations:
            subject_object_pair = (relation['subject'], relation['object'])
            if subject_object_pair not in unique_subject_object_pairs or relation['confidence'] > unique_subject_object_pairs[subject_object_pair]['confidence']:
                unique_subject_object_pairs[subject_object_pair] = relation

        all_extraction = list(unique_subject_object_pairs.values())

        # Reset current_query for the next iteration
        current_query = None

        # Look for the next highest-confidence query that hasn't been used
        for relation in extracted_relations:
            new_query = f"{relation['subject']} {relation['object']}"
            if new_query not in queries_used and relation['relation'] != "no_relation":
                current_query = new_query
                queries_used.add(new_query)
                # print(f"Next query selected based on highest confidence: {new_query}")
                break  # Break after selecting the highest-confidence new query

        if not current_query:
            # No new queries can be extracted
            print("No more new queries can be extracted based on the relations found. Stopping the process.")
            return

        print("=====Summary======")

    # Final output
    if len(all_extraction) >= tuple_num:
        print("Final extracted relations:")
        print(f"Total number of relations extracted: {len(all_extraction)}")
        print("=================================================================================================")
        print("{:<30} {:<40} {:<30} {:<10}".format("Subject", "Relation","Object", "Confidence"))
        print("=================================================================================================")
        for relation in sorted(all_extraction, key=lambda x: x['confidence'], reverse=True):
            print("{:<30} {:<40} {:<30} {:<10}".format(relation['subject'], relation['relation'], relation['object'], "{:.8f}".format(relation['confidence'])))
        print("=================================================================================================")
        print(f"Total Number of iterations = {iter}")
    else:
        print("No tuples extracted. Program stops.")

# def iterative_extraction(search_api, relation_extractor, initial_query, queries_used, all_extraction, tuple_num):
#     queries_used.add(initial_query)
#     current_query = initial_query
#     iter = 0

#     while len(all_extraction) < tuple_num:
#         print(f"================ Iteration {iter}:Current Query Processing: {current_query} ======================")
#         iter+=1

#         # Update search_api with the current query
#         search_api.query = current_query
#         extracted_relations = search_api.process_and_extract_relations(relation_extractor, search_api.relation_id, search_api.confidence)

#         if not extracted_relations:
#             print("No new tuples extracted. Not enough k tuples found.")
#             return

#         # Sort extracted relations by confidence, descending
#         extracted_relations.sort(key=lambda x: x['confidence'], reverse=True)

#         # Extend the all_extraction with newly extracted relations
#         all_extraction.extend(extracted_relations)

#         '''
#         # Remove Duplicates of SpanBERT. Convert inner lists to tuples before converting to set
#         # all_extraction_tuples = [tuple(relation) for relation in all_extraction]

#         # # Remove duplicates while preserving order
#         # seen = set()
#         # all_extraction_unique = [x for x in all_extraction_tuples if (tuple(x[0:2]) not in seen) and not seen.add(tuple(x[0:2]))]

#         # # Convert back to a list of lists
#         # all_extraction = [list(relation) for relation in all_extraction_unique]
#         '''

#         # Reset current_query for the next iteration
#         current_query = None

#         # Look for the next highest-confidence query that hasn't been used
#         for relation in extracted_relations:
#             new_query = f"{relation['subject']} {relation['object']}"
#             if new_query not in queries_used and relation['relation'] != "no_relation":
#                 current_query = new_query
#                 queries_used.add(new_query)
#                 # print(f"Next query selected based on highest confidence: {new_query}")
#                 break  # Break after selecting the highest-confidence new query

#         if not current_query:
#             # No new queries can be extracted
#             print("No more new queries can be extracted based on the relations found. Stopping the process.")
#             return

#         print("=====Summary======")

#     # Final output
#     if all_extraction:
#         print("Final extracted relations:")
#         print(f"Total number of relations extracted: {len(all_extraction)}")
#         print("=================================================================================================")
#         print("{:<30} {:<40} {:<30} {:<10}".format("Subject", "Relation","Object", "Confidence"))
#         print("=================================================================================================")
#         for relation in sorted(all_extraction, key=lambda x: x['confidence'], reverse=True):
#             print("{:<30} {:<40} {:<30} {:<10}".format(relation['subject'], relation['relation'], relation['object'], "{:.8f}".format(relation['confidence'])))
#         print("=================================================================================================")
#         print(f"Total Number of iterations = {iter}")
#     else:
#         print("No tuples extracted. Program stops.")


def iterative_extraction_gemeni(search_api, relation_extractor, initial_query, queries_used, all_extraction, tuple_num):
    queries_used.add(initial_query)
    current_query = initial_query
    iter_count = 0

    while len(set(all_extraction)) < tuple_num:
        print(f"\n=============== Iteration {iter_count}: Current query - {current_query} ====================")
        iter_count += 1

        # Update search_api with the current query
        search_api.query = current_query
        extracted_relations = search_api.process_and_extract_relations(relation_extractor, search_api.relation_id, search_api.confidence)

        if not extracted_relations:
            print("No new tuples extracted. Not enough k tuples found.")
            break
   
        # Assuming all_extraction is initially a list of extracted relations
        all_extraction.extend(extracted_relations)

        # Normalize and remove duplicates
        normalized_extractions = {(relation[0].strip(), relation[1].strip(), relation[2].strip()) for relation in all_extraction}

        # Convert back to a list, if needed
        all_extraction = list(normalized_extractions)

        potential_queries = [f"{relation[0]} {relation[2]}" for relation in extracted_relations if f"{relation[0]} {relation[2]}" not in queries_used]

        if potential_queries:
            next_query = random.choice(potential_queries)
            queries_used.add(next_query)
            current_query = next_query
            print(f"Randomly selected new query for next iteration: {current_query}")
        else:
            print("No new unique queries can be generated from extracted relations. Stopping the process.")
            return

    if len(all_extraction) < tuple_num:
        print(f"Not enough k tuples found. Only {len(all_extraction)} tuples extracted.")
    else:
        print("\nFinal extracted relations:")
        print(f"Total number of relations extracted: {len(all_extraction)}")
        print(f"Only produced the required number ({tuple_num}) of tuple relations")
        print("==========================================================================================")
        print("{:<50} {:<40} {:<50}".format("Subject", "Relation", "Object"))
        print("==========================================================================================")
        for relation in all_extraction[:tuple_num]:
            print("{:<50} {:<40} {:<50}".format(relation[0], relation[1], relation[2]))
        print("==========================================================================================")
        print(f"Total # of iterations = {iter_count}")

if __name__ == '__main__':

    # search_type = "-gemini"
    # api_key = "AIzaSyC5v2l8vS4TZEIgsOeyrLUeBATHkmKBf58"
    # engine_id = "62edd23ecda9c4041"
    # # gemini_api_key = "AIzaSyDyeq4E5dNYsQqzXz3X6B_q7kfKUir9pcE" # AIzaSyDyeq4E5dNYsQqzXz3X6B_q7kfKUir9pcE # AIzaSyD9otDl9zplDgPvLkCev0m3QTzZ_UzDUsg
    # gemini_api_key_list = ["AIzaSyDyeq4E5dNYsQqzXz3X6B_q7kfKUir9pcE", "AIzaSyD9otDl9zplDgPvLkCev0m3QTzZ_UzDUsg", "AIzaSyD9otDl9zplDgPvLkCev0m3QTzZ_UzDUsg"]
    # gemini_api_key = gemini_api_key_list[2]  # AIzaSyDyeq4E5dNYsQqzXz3X6B_q7kfKUir9pcE # AIzaSyD9otDl9zplDgPvLkCev0m3QTzZ_UzDUsg # AIzaSyD9otDl9zplDgPvLkCev0m3QTzZ_UzDUsg
    # relation_id = "4"
    # confidence = "0.7"
    # query = "bill gates microsoft"
    # # # query = "bill gates microsoft"
    # tuple_num = "10"

    if len(sys.argv) != 9:
         print("Please enter: python3 project2.py [-spanbert|-gemini] <google api key> <google engine id> <google gemini api key> <r> <t> <q> <k>")
         sys.exit()

    # # _, api_key, engine_id, precision, query = sys.argv
    _, search_type, api_key, engine_id, gemini_api_key, relation_id, confidence, query, tuple_num = sys.argv

    relation_entity_types = {
        1: {"subj": "PERSON", "obj": "ORGANIZATION"},  # Schools_Attended
        2: {"subj": "PERSON", "obj": "ORGANIZATION"},  # Work_For
        3: {"subj": "PERSON", "obj": ["LOCATION", "CITY", "STATE_OR_PROVINCE", "COUNTRY"]},  # Live_In
        4: {"subj": "ORGANIZATION", "obj": "PERSON"}  # Top_Member_Employees
    }
    queries_used = set()
    queries_used.add(query)
    all_extraction = []

    if search_type=="-spanbert":
        relation_extractor = BertRelationExtraction("en_core_web_lg", "./pretrained_spanbert", relation_entity_types, confidence)
        search_api = GoogleSearchAPI(search_type, api_key, engine_id, gemini_api_key, int(relation_id), float(confidence), query, int(tuple_num))
        iterative_extraction(search_api, relation_extractor, query, queries_used, all_extraction, int(tuple_num))
    elif search_type=="-gemini":
        relation_extractor = GeminiRelationExtraction("en_core_web_lg", gemini_api_key, relation_entity_types, relation_id)
        search_api = GoogleSearchAPI(search_type, api_key, engine_id, gemini_api_key, int(relation_id), float(confidence), query, int(tuple_num))
        iterative_extraction_gemeni(search_api, relation_extractor, query, queries_used, all_extraction, int(tuple_num))
    else:
        print("Either -spanbert/-gemini")