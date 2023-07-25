import re

def insert_br_before_long_words(input_string, max_consecutive_chars=20):
    words = re.findall(r'\S+|[.,!?;]', input_string)  # Split words and keep punctuation marks
    result = []
    current_line_length = 0

    for item in words:
        if re.match(r'\S+', item):  # If it's a word
            word_length = len(item)
            if current_line_length + word_length > max_consecutive_chars:
                result.append('<br> ')
                current_line_length = 0

            result.append(item + ' ')
            current_line_length += word_length
        else:  # If it's a punctuation mark
            result.append(item + ' ')
            current_line_length += 1

    return ''.join(result)

# Test the function
input_string = "This is a test string, for inserting br tags before long words like hippopotamus and antidisestablishmentarianism!"
output_string = insert_br_before_long_words(input_string, max_consecutive_chars=20)
print(output_string)
