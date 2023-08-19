import translators as ts

print(ts.translators_pool)

res = ts.google("Welcome to our tutorial!", to_language='fr')
print(res)