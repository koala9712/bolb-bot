from itertools import product


# get all combos of cases
low = "bolb "
up = low.upper()
m = zip(low, up)


db_enabled = False
colors = [0x00FFEA]
prefix = set("".join(m) for m in product(*m))
helpindex = "bolb."
helpprefix = True
