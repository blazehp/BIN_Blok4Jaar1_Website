import numpy as np
from matplotlib import pyplot as plt


def create_piechart(values: dict, title: str):
    print(list(values.keys()))
    keys = np.array(list(values.keys()))
    print(keys)
    plt.pie(values.values(), labels=keys)
    plt.title(title)

    plt.show()


def create_sunburst_chart(values: list[tuple],
                          title: str, level=0,
                          total=np.pi * 2, ax=None):
    ax = ax or plt.subplot(111, title=title, projection='polar')

    if level == 0 and len(values) == 1:
        label, values, subnodes = values[0]
        ax.bar([0], [0, 5], [np.pi * 2])
        ax.text(0, 0, label, ha='center', va='center')
        create_sunburst_chart(subnodes, total=total, title=title,ax=ax)
    elif values:
        diameter = np.pi * 2 / total
        labels = []
        widths = []
        for label, value, subnodes in values:
            labels.append(label)
            widths.append(value * diameter)


if __name__ == '__main__':
    species_dict = {
        "homo sapiens": 5,
        "lasius niger": 6,
        "Griseotyrannus aurantioatrocristatus": 42,
        "boops boops": 8

    }
    create_piechart(species_dict, title="testdata")
    data = [
        ('eukarya', 100, [
            ('fungi', 70, [
                ('Rozellida', 40, []),
                ('Aphelida', 20, []),
                ('Chytridiomyceta', 5, []),
            ]),
            ('animalia', 15, [
                ('Chordate', 6, [
                    ('Mammal', 4, []),
                    ('aves', 1, []),

                ]),
                ('Echinoderm', 4, []),
                ('Hemichordate', 2, []),
                ('Mollusca', 1, []),
                ('Brachiopod', 1, []),
                ('Phoronid', 1, []),
            ]),
        ]),
    ]
    create_sunburst_chart(data, title="testdata")
