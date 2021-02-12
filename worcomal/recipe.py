from collections import Counter
import os

import numpy as np
import scipy.cluster.hierarchy as hac
import scipy.spatial.distance as ssd
from scipy.stats.mstats import gmean

import json
from tqdm import tqdm

def group_by_english(compounds: list, f2e: dict):
    grouped = {}
    for c in compounds:
        engs = f2e[c.lang, c.word]
        for e in engs:
            if e not in grouped:
                grouped[e] = []
            grouped[e].append(c)
    return grouped


def read_stopwords():
    stop = set()
    with open(os.path.dirname(__file__) + "/data/stopwords.txt") as fin:
        for line in fin:
            stop.add(line.strip())
    return stop


STOP_WORDS = read_stopwords()


def make_recipe(compounds: list, f2e: dict):
    '''recipe for a single concept'''
    comp_counts = count_components(compounds, f2e)

    # keep good components
    comp_counts = {comp: count
                   for (comp, count) in comp_counts.items()
                   if count >= 2 and comp not in STOP_WORDS}  # todo: filter components elsewhere
    components = sorted(comp_counts.keys())

    if len(components) < 2:
        return [], [], {}

    distances = compute_component_distances(compounds, components, f2e)
    left, right = cluster_components(distances, components)
    return left, right, comp_counts


def count_components(compounds, f2e):
    '''for a single concept'''
    comps_with_lang = []
    for c in compounds:
        for left in f2e[c.lang, c.left]:
            comps_with_lang.append((left, c.lang))
        for right in f2e[c.lang, c.right]:
            comps_with_lang.append((right, c.lang))

    # the same component may exist in multiple languages
    comps_with_lang = list(set(comps_with_lang))
    components = [comp for (comp, lang) in comps_with_lang]
    return Counter(components)


def compute_component_distances(compounds: list, components: list, f2e: list):
    comp_set = set(components)

    lefts = set()
    rights = set()
    for c in compounds:
        for e in f2e[c.lang, c.left]:
            if e in comp_set:
                lefts.add(e)
        for e in f2e[c.lang, c.right]:
            if e in comp_set:
                rights.add(e)

    c2i = {x: i for (i, x) in enumerate(components)}
    dist = np.zeros([len(components), len(components)]) + 0.5

    lefts = [c2i[c] for c in lefts]
    rights = [c2i[c] for c in rights]

    for l1 in lefts:
        for l2 in lefts:
            dist[l1, l2] = 0
            dist[l2, l1] = 0
    for r1 in rights:
        for r2 in rights:
            dist[r1, r2] = 0
            dist[r2, r1] = 0
    for l in lefts:
        for r in rights:
            dist[l, r] = 1
            dist[r, l] = 1

    for i in range(len(components)):
        dist[i, i] = 0

    return dist


def cluster_components(distances, components):
    z = hac.linkage(ssd.squareform(distances), "average")
    assignments = hac.cut_tree(z, n_clusters=[2])
    assert len(assignments) == len(components)

    left = []
    right = []
    for (comp, a) in zip(components, assignments):
        if a == 1:
            left.append(comp)
        else:
            right.append(comp)
    return (left, right)


def make_and_save_recipes(output_file, compounds, f2e):
    grouped = group_by_english(compounds, f2e)
    with open(output_file, 'w') as fout:
        for concept in tqdm(grouped):
            left, right, counts = make_recipe(grouped[concept], f2e)
            if left != [] and right != []:
                d = {
                    'concept': concept,
                    'left': left,
                    'right': right,
                    'counts': counts
                }
                print(json.dumps(d), file=fout)


def read_recipes(fn: str):
    recipes = {}
    with open(fn) as fin:
        for line in fin:
            d = json.loads(line)
            recipes[d['concept']] = d
