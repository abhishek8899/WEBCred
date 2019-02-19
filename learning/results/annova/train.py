# trie
# autocomplete()
# A = [ ]


def comprefix(a, b):

    if len(a) > len(b):
        temp = a
        a = b
        b = a

    count = 0

    for index, elem in enumerate(a):
        if elem == b[index]:
            count += 1
        else:
            break

    return count


def writeword(elem, diff):
    word = elem[:diff]
    count = 0
    for i in elem[diff:]:
        word += i
        count += 1
        if autocomplete(word):
            break

    return count


# TODO when len(A)==1
if len(A) == 1:
    count = 1
else:
    diff = comprefix(A[0], A[1])
    last = count = diff
    for index, elem in enumerate(A[1:]):
        if index + 1 < len(A):
            j = index + 1

            diff = comprefix(elem, A[j])

            count += 2 * writeword(elem, diff)

            # backspace
            # count += abs(diff - last)
            # last = diff

        # TODO think for the boundry case when j==len(A)
        else:
            count += writeword(elem, last)
