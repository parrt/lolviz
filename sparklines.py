import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import tempfile

from io import BytesIO

# inspired by Mark Needham's blog
# https://markhneedham.com/blog/2017/09/23/python-3-create-sparklines-using-matplotlib/

def sparkline(data, filename, fill=False, figsize=(4, 0.25), **kwags):
    """
    Save a sparkline image
    """
    fig, ax = plt.subplots(1, 1, figsize=figsize, **kwags)
    ax.plot(data, linewidth=.5)
    for k,v in ax.spines.items():
        v.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])

    # ax.plot(len(data) - 1, data[len(data) - 1], 'r.')

    if fill:
        ax.fill_between(range(len(data)), data, len(data)*[min(data)], alpha=0.1)

    plt.savefig(filename, transparent=True, bbox_inches='tight', dpi = 300)
    plt.show()


if __name__ == "__main__":

    values = [7,10,12,18,2,8,10,6,7,12],
    fig = plt.figure()
    plt.plot(values, linewidth=.5)
    plt.show()

    # tmp = tempfile.gettempdir()
    # sparkline(values, "/tmp/foo.png")
