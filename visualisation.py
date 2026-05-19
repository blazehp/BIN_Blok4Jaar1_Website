from matplotlib import pyplot as plt
import numpy as np

def create_piechart(values: dict, title: str):
    print(list(values.keys()))
    keys = np.array(list(values.keys()))
    print(keys)
    plt.pie(values.values(), labels= keys)
    plt.title(title)

    plt.show()

if __name__ == '__main__':
    dict = {
        "homo sapiens": 5,
        "lasius niger": 6,
        "Griseotyrannus aurantioatrocristatus": 42,
        "boops boops": 8

    }
    create_piechart(dict,title= "testdata")

