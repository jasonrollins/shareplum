# This is a group of small functions
# used to work with a list of dictionaries
from typing import Any
from typing import Dict
from typing import List


def changes(new_cmp_dict: Dict, old_cmp_dict: Dict, id_column: str, columns: List[str]) -> List[Dict]:
    """Return a list dict of the changes of the
       rows that exist in both dictionaries
       User must provide an ID column for old_cmp_dict
    """

    update_ldict = []
    same_keys = set(new_cmp_dict).intersection(set(old_cmp_dict))
    for same_key in same_keys:
        # Get the Union of the set of keys
        # for both dictionaries to account
        # for missing keys
        old_dict = old_cmp_dict[same_key]
        new_dict = new_cmp_dict[same_key]

        update_dict = {}
        for dict_key in columns:
            old_val = old_dict.get(dict_key, "NaN")
            new_val = new_dict.get(dict_key, "NaN")
            if old_val != new_val and new_val != "NaN":
                if id_column:
                    try:
                        update_dict[id_column] = old_dict[id_column]
                    except KeyError as e:
                        print(f"Input Dictionary 'old_cmp_dict' must have ID column: {e}")
                update_dict[dict_key] = new_val
        if update_dict:
            update_ldict.append(update_dict)
    return update_ldict


def unique(new_cmp_dict: Dict, old_cmp_dict: Dict) -> List:
    """Return a list dict of
       the unique keys in new_cmp_dict
    """
    newkeys = set(new_cmp_dict)
    oldkeys = set(old_cmp_dict)
    unique = newkeys - oldkeys
    unique_ldict = []
    for key in unique:
        unique_ldict.append(new_cmp_dict[key])
    return unique_ldict


def full_dict(ldict: Dict, keys: Any) -> Dict:
    """Return Comparison Dictionaries
       from list dict on keys
       keys: a list of keys that when
       combined make the row in the list unique
    """
    if type(keys) == str:
        keys = [keys]
    else:
        keys = keys

    cmp_dict = {}
    for line in ldict:
        index: List[str] = []
        for key in keys:
            index.append(str(line.get(key, "")))
        index_str: str = "-".join(index)
        cmp_dict[index_str] = line

    return cmp_dict
