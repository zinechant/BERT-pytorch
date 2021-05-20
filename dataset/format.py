import os
import random
from tqdm import tqdm


def trim(words, num):
    if not num:
        return words
    snum = random.randint(0, num)
    enum = len(words) - (num - snum)
    return words[snum:enum]


def format(fi, fo, max_seq_len, short_prob):
    """
    Format text files into sequence pairs.
    The maskings and next setence are online so not considered here
    """
    line_words = []

    lines = []
    words = 0
    seq_words = (random.randint(2, max_seq_len - 3)
                 if random.random() < short_prob else max_seq_len - 3)

    pbar = tqdm(total=os.path.getsize(fi.name))

    while True:
        if not line_words:
            line = fi.readline()
            pbar.update(len(line))
            if not line:
                break
            line_words = line.strip().split()

        if words < 2 or (len(line_words) >> 1) < (seq_words - words):
            lines.append(line_words)
            words += len(line_words)
            line_words = []
        if words + len(line_words) >= seq_words:
            awords = []
            bwords = []
            if len(lines) == 1:
                split = random.randint(1, words - 1)
                awords = lines[0][:split]
                bwords = lines[0][split:]
            else:
                split = random.randint(1, len(lines) - 1)
                for i in range(split):
                    awords.extend(lines[i])
                for i in range(split, len(lines)):
                    bwords.extend(lines[i])

            extra = 3 + len(awords) + len(bwords) - max_seq_len
            if extra > 0:
                ra = random.randint(max(0, extra + 1 - len(bwords)),
                                    min(extra,
                                        len(awords) - 1))
                rb = extra - ra
                awords = trim(awords, ra)
                bwords = trim(bwords, rb)

            import pdb
            assert (len(awords) + len(bwords) + 3 <=
                    max_seq_len), pdb.set_trace()
            fo.write("%s\t%s\n" % (" ".join(awords), " ".join(bwords)))

            lines = []
            words = 0
            seq_words = (random.randint(2, max_seq_len - 3)
                         if random.random() < short_prob else max_seq_len - 3)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--text_path", required=True, type=str)
    parser.add_argument("-c", "--corpus_path", required=True, type=str)
    parser.add_argument("-l", "--seq_len", type=int, default=64)
    parser.add_argument("-s", "--short_prob", type=float, default=0.1)
    parser.add_argument("-e", "--encoding", type=str, default="utf-8")

    args = parser.parse_args()

    with open(args.text_path, 'r', encoding=args.encoding) as fi:
        with open(args.corpus_path, "w", encoding=args.encoding) as fo:
            format(fi, fo, args.seq_len, args.short_prob)
