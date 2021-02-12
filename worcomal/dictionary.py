def read_dictionary_f2e(fn):
    f2e = {}
    with open(fn) as fin:
        for line in fin:
            arr = line.split('\t')
            lang = arr[0]
            f = arr[2]
            e = arr[1]
            if (lang, f) not in f2e:
                f2e[lang, f] = []
            f2e[lang, f].append(e)
    return f2e


def add_english_words(f2e):
    for definitions in list(f2e.values()):
        for defin in definitions:
            if ("eng", defin) not in f2e or defin not in f2e["eng", defin]:
                f2e["eng", defin] = [defin]