import argparse
import csv

from normalization.normalizer import Normalizer

def tobool(s):
    """helper method to parse bools"""
    try:
        int_s = int(s)
        return bool(int_s)
    except:
        pass
    if s.lower()[0] == "t":
        return True
    elif s.lower()[0] == "f":
        return False
    else:
        raise ValueError("cannot find bool")

def toint(s):
    try:
        return int(s)
    except:
        if not s:
            return None
        raise ValueError("cannot convert to int")


def read_input(input_path):
    samples = []
    with open(input_path, 'rU') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sample = {
                "input" : {"section" : row["section"], "row" : row["row"]},
                "expected" : {"section_id" : toint(row["n_section_id"]), "row_id" : toint(row["n_row_id"]), "valid" : tobool(row["valid"])}
            }
            samples.append(sample)
    return samples

def _section_match(s1, s2):
    return s1 == s2 or (s1 is None and s2 is None)

def _row_match(r1, r2):
    return r1 == r2 or (r1 is None and r2 is None)

def grade_match(match, verbose=False):
    e_sid, e_rid, e_valid = match["expected"]["section_id"], match["expected"]["row_id"], match["expected"]["valid"]
    o_sid, o_rid, o_valid = match["output"]["section_id"], match["output"]["row_id"], match["output"]["valid"]
    i_s = match["input"]["section"]
    i_r = match["input"]["row"]

    # if expected is valid...
    sm = _section_match(e_sid, o_sid)
    rm = _row_match(e_rid, o_rid)
    vm = e_valid == o_valid
    pts = 0

    if e_valid:
        if sm and rm and vm:
            if verbose:
                print ".. ok"
            pts = 1

        if not vm:
            if verbose:
                print ".. {}:{} marked invalid, should be {}:{}".format(i_s, i_r, e_sid, e_rid)
            pts = 0

        if vm and (not sm or not rm):
            if verbose:
                print ".. {}:{} WRONG!, marked {}:{}, should be {}:{}".format(i_s, i_r, o_sid, o_rid, e_sid, e_rid)
            pts = -5

    if not e_valid:
        if sm and rm and vm:
            if verbose:
                print ".. ok"
            pts = 1

        if not vm:
            if verbose:
                print ".. {}:{} WRONG! Marked valid, should be invalid".format(i_s, i_r)
            pts = -5
    return pts

def grade_samples(normalizer, samples, verbose=False):
    matched = []
    for sample in samples:
        sid, rid, valid = normalizer.normalize(sample["input"]["section"], sample["input"]["row"])
        e_sid, e_rid, e_valid = sample["expected"]["section_id"], sample["expected"]["row_id"], sample["expected"]["valid"]
        sample["output"] = {"section_id" : sid, "row_id" : rid, "valid" : valid}
        matched.append(sample)

    # grade matched values
    total_pts = 0
    max_pts = 0
    for match in matched:
        pts = grade_match(match, verbose=verbose)
        max_pts += 1
        total_pts += pts

    print "{} / {}".format(total_pts, max_pts)
    return total_pts, max_pts


def grade(normalizer, input_path):
    samples = read_input(input_path)
    return grade_samples(normalizer, samples, verbose=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='grader for seatgeek SectionNormalization code test')
    parser.add_argument('--manifest', default=None, help='path to manifest file')
    parser.add_argument('--input', default=None, help='path to input file')
    parser.add_argument('--section', default=None, help='section input (for testing)')
    parser.add_argument('--row', default=None, help='row input (for testing)')

    args = parser.parse_args()

    assert args.manifest

    normalizer = Normalizer()
    normalizer.read_manifest(args.manifest)

    if args.section and args.row:
        section_id, row_id, valid = normalizer.normalize(args.section, args.row)
        print """
        Input:
            [section] {}\t[row] {}
        Output:
            [section_id] {}\t[row_id] {}
        Valid?:
            {}
        """.format(args.section, args.row, section_id, row_id, valid)

    elif args.input:
        grade(normalizer, args.input)
