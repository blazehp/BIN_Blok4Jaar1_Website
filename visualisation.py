from matplotlib import pyplot as plt
import numpy as np

def create_piechart(values: dict, title: str):
    print(list(values.keys()))
    keys = np.array(list(values.keys()))
    print(keys)
    plt.pie(values.values(), labels= keys)
    plt.title(title)

    plt.show()

<<<<<<< Updated upstream
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
def create_scatterplot(values: dict[str, int], title: str = "scatterplot",x_label: str = " ", y_label: str = " "):
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
=======
if __name__ == '__main__':
    dict = {
        "homo sapiens": 5,
        "lasius niger": 6,
        "Griseotyrannus aurantioatrocristatus": 42,
        "boops boops": 8
>>>>>>> Stashed changes

    }
    create_piechart(dict,title= "testdata")

