import matplotlib.pyplot as plt
import numpy as np



def create_piechart(values: dict[str,int], title: str = ""):
    plt.pie(values.values(), labels=values.keys())
    plt.title(title)
    plt.show()




if __name__ == "__main__":
    dict = {
        "dingdong":1,
        "ding":2,
        "test": 3,
        "qwerty":3

    }
    create_piechart(dict)
