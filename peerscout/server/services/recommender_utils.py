def sorted_manuscript_scores_descending(manuscript_scores_list):
    return list(reversed(sorted(manuscript_scores_list, key=lambda score: (
        score['combined'] or 0,
        score['keyword'] or 0,
        score['similarity'] or 0
    ))))
