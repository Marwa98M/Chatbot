import re


def extract_session_id(session_str: str):
    match = re.search(r"/sessions/(.*?)/contexts/", session_str)
    if match:
        extracted_string = match.group(1)
        return extracted_string
    return ""

def get_str_from_food_dict(food_dict):
    print(food_dict.values())



    return ', '.join(food_dict).join(food_dict.values())


#
if __name__ == "__main__":
    dict = {'Milk': 1, 'Cheese': 2, 'Biscuits': 3}
    print(get_str_from_food_dict(dict))

    #print(extract_session_id("projects/mira-chatbot-for-food-del-iwup/agent/sessions/362e60d4-0f2d-37cc-8fb9-9535fb8169d9/contexts/ongoing-order")




