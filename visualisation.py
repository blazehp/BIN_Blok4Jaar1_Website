import matplotlib.pyplot as plt


def create_piechart(values: dict[str, int], title: str = "piechart"):
    if not values:
        raise ValueError("values are empty can't draw chart")
    labels = values.keys()
    fig, ax = plt.subplots()
    ax.pie(values.values(), labels=labels)
    plt.title(title)
    plt.savefig(f"graphs/{title}.svg")


def create_barplot(values: dict[str, int],
                   title: str = "barplot",
                   x_label: str = " ", y_label: str = " "):
    if not values:
        raise ValueError("values are empty ,can't draw chart")
    fig, ax = plt.subplots()
    ax.bar(values.keys(), values.values())
    plt.title(title)
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.savefig(f"graphs/{title}.svg")


def create_scatterplot(values: dict[str, int], title: str = "scatterplot", x_label: str = " ", y_label: str = " "):
    if not values:
        raise ValueError("values are empty can't draw chart")
    fig, ax = plt.subplots()
    ax.scatter(values.keys(), values.values())
    plt.title(title)
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.savefig(f"graphs/{title}.svg")


if __name__ == "__main__":
    data = {
        "dingdong": 1,
        "ding": 2,
        "test": 3,
        "qwerty": 3

    }
    create_piechart(data)
    create_barplot(data)
