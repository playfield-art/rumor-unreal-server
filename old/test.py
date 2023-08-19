import translators as ts


query_text = "Welcome to our tutorial!"
for i in range(10000):
    res = ts.translate_text(query_text, 'google', 'auto', 'nl')
    print(res + str(i))