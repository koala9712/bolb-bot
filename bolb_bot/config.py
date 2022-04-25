from itertools import product


# get all combos of cases
low = "bolb "
up = low.upper()
m = zip(low, up)


db_name = "bolb"
colors = [0x00FFEA]
prefix = set("".join(m) for m in product(*m))
helpindex = "bolb."
helpprefix = True
