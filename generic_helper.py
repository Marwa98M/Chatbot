import re


def extract_session_id(session_str: str):
    match = re.search(r"/sessions/(.*?)/contexts/", session_str)
    if match:
        extracted_string = match.group(1)
        return extracted_string
    return ""

def get_str_from_food_dict(food_dict):
    fulfillment_text = f"So far you have:"
    i = 1
    for key, value in food_dict.items():
        fulfillment_text += f"{int(value)} {key}"
        if i < len(food_dict):
            fulfillment_text += ', and '
        i = i+1
    return fulfillment_text
if __name__ == "__main__":
    print(extract_session_id("projects/mira-chatbot-for-food-del-iwup/agent/sessions/362e60d4-0f2d-37cc-8fb9-9535fb8169d9/contexts/ongoing-order")
)