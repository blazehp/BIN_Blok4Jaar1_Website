import matplotlib.pyplot as plt


def create_piechart(values: dict[str, int], title: str = "piechart"):
    if not values:
        raise ValueError("values are empty can't draw nothing")
    labels = values.keys()
    fig, ax = plt.subplots()
    ax.pie(values.values(), labels=labels)
    plt.title(title)
    plt.plot(values.keys(), values.values())
    plt.savefig(f"graphs/{title}.svg")


if __name__ == "__main__":
    dict = {
        "dingdong": 1,
        "ding": 2,
        "test": 3,
        "qwerty": 3

    }
    create_piechart(dict)
