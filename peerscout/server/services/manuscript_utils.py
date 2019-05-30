from itertools import groupby


def _select_preferred_manuscript_and_alternatives(manuscripts):
    if len(manuscripts) == 1:
        return manuscripts[0]
    preferred_manuscript = next(
        (m for m in manuscripts if m.get('abstract')),
        manuscripts[0]
    )
    preferred_manuscript_id = preferred_manuscript['manuscript_id']
    return {
        **preferred_manuscript,
        'alternatives': [m for m in manuscripts if m['manuscript_id'] != preferred_manuscript_id]
    }


def duplicate_manuscript_titles_as_alternatives(manuscripts):
    if not manuscripts or len(manuscripts) < 2:
        return manuscripts

    def get_title(m):
        return m.get('title', '')
    manuscripts_by_title = groupby(
        sorted(manuscripts, key=get_title),
        get_title
    )
    return [
        _select_preferred_manuscript_and_alternatives(list(manuscripts_with_same_title))
        for _, manuscripts_with_same_title in manuscripts_by_title
    ]
