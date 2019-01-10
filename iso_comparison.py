import numpy as np
from sys import argv
from matplotlib import pyplot as plt
from phonecal import io, gain

folders = io.path_from_input(argv)
colours = ["black", "red", "xkcd:purple", "xkcd:olive", "xkcd:lilac", "xkcd:custard", "xkcd:peach"]

plt.figure(figsize=(6, 4), tight_layout=True)

xmax = 0

for c, folder in zip(colours, folders):
    root, images, stacks, products, results = io.folders(folder)
    phone = io.read_json(root/"info.json")

    iso_max = phone["software"]["ISO max"]

    products_iso = products/"iso"

    lookup_table = np.load(products_iso/"lookup_table.npy")
    data         = np.load(products_iso/"data.npy"        )

    plt.errorbar(data[0], data[1], yerr=data[2], fmt=f"o", c=c, label=phone["device"]["name"])
    plt.plot(*lookup_table, c=c)

    xmax = max(xmax, iso_max)

    print(phone["device"]["manufacturer"], phone["device"]["name"])

plt.xlabel("ISO speed")
plt.ylabel("Normalization")
plt.xlim(xmin=0)
plt.ylim(ymin=0)
plt.grid(True)
plt.legend(loc="best")
plt.savefig("results/iso_comparison.pdf")
plt.show()
plt.close()
