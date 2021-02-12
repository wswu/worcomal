import worcomal
from worcomal.dictionary import *
from worcomal.compound import *
from worcomal.stats import count_methods_per_lang
from worcomal.recipe import *

f2e = read_dictionary_f2e("/export/c12/wwu/database/wiktionary.tsv")
add_english_words(f2e)

concat = find_compounds(f2e, ['concat'])
write_compounds("output/concat.txt", compounds)

glue = find_compounds(f2e, ['glue'])
write_compounds("output/glue.txt", glue)

dropl = find_compounds(f2e, ['dropl'])
write_compounds("output/dropl.txt", dropl)

compounds = read_compounds('output/concat+glue.txt')
make_and_save_recipes('output/recipes3.txt', compounds, f2e)

save_methods_per_lang('output/methods', compounds)
save_components_per_lang('output/components', compounds)
