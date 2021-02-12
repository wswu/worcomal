import os
from collections import Counter


def count_methods_per_lang(compounds: list):
    counts = {}
    for c in compounds:
        if c.lang not in counts:
            counts[c.lang] = Counter()
        counts[c.lang][c.method, c.middle] += 1
    return counts


def save_methods_per_lang(output_folder, compounds, low_data_threshold=5, keep_threshold=2, length_threshold=5):
    """
    low_data_threshold: keep all if the number of methods is <= this number
    keep_threshold: discard if count of this method is < this number
    length_threshold: discard if length of glue is > this number
    """
    os.makedirs(output_folder, exist_ok=True)
    cm = count_methods_per_lang(compounds)
    for lang in cm:
        keys = list(cm[lang].keys())
        if len(keys) <= low_data_threshold:
            continue
        for method, middle in keys:
            if cm[lang][method, middle] < keep_threshold or len(middle) > length_threshold:  # todo: set cutoff
                del cm[lang][method, middle]

    for lang in cm:
        with open(os.path.join(output_folder, lang), 'w') as fout:
            for (method_middle, count) in cm[lang].most_common():
                print(' '.join(method_middle), count, sep='\t', file=fout)


def count_components_per_lang(compounds: list):
    counts = {}
    for c in compounds:
        if c.lang not in counts:
            counts[c.lang] = Counter()
        counts[c.lang][c.left] += 1
        counts[c.lang][c.right] += 1
    return counts


def save_components_per_lang(output_folder, compounds, low_data_threshold=10, keep_threshold=2):
    """
    low_data_threshold: keep all if the number of components is <= this number
    keep_threshold: discard if count of this component is < this number
    """
    cc = count_components_per_lang(compounds)
    os.makedirs(output_folder, exist_ok=True)

    for lang in cc:
        keys = list(cc[lang].keys())
        if len(keys) <= low_data_threshold:
            continue
        for comp in keys:
            if cc[lang][comp] < keep_threshold:
                del cc[lang][comp]

    for lang in cc:
        with open(os.path.join(output_folder, lang), 'w') as fout:
            for (comp, count) in cc[lang].most_common():
                print(comp, count, sep='\t', file=fout)

