import numpy as np
from matplotlib import pyplot as plt


def create_piechart(values: dict, title: str):
    if not values:
        raise ValueError("values are empty")
    if not isinstance(values, dict):
        raise ValueError("values are not a dict")
    if not isinstance(title, str):
        raise ValueError("title is not a string")
    try:
        keys = np.array(list(values.keys()))

        plt.pie(values.values(), labels=keys)
        plt.title(title)
        plt.savefig("static/" + title + ".svg")

    except TypeError as e:
        print("data is formatted wrong make sure all values are numerical")
    finally:
        plt.show()


def create_sunburst_chart(nodes: list[tuple],
                          title: str = "a Sunburst diagram(please insert a title next time)", level=0,
                          total=np.pi * 2, ax=None, offset=0):
    ax = ax or plt.subplot(111, title=title, projection='polar')

    if level == 0 and len(nodes) == 1:
        label, value, subnodes = nodes[0]
        ax.bar([0], [0.5], [np.pi * 2])
        ax.text(0, 0, label, ha='center', va='center')
        create_sunburst_chart(subnodes, total=value, title=title, ax=ax, level=level + 1)
    elif nodes:
        diameter = np.pi * 2 / total
        labels = []
        widths = []
        local_offset = offset
        for label, value, subnodes in nodes:
            labels.append(label)
            widths.append(value * diameter)
            create_sunburst_chart(subnodes, total=total, title=title, ax=ax, level=level + 1, offset=local_offset)
            local_offset += value
        values = np.cumsum([offset * diameter] + widths[:-1])
        heights = [1] * len(nodes)
        bottoms = np.zeros(len(nodes)) + level - 0.5
        rects = ax.bar(values, heights, widths, bottoms, linewidth=1, align='edge', edgecolor='black')
        for rect, label in zip(rects, labels):
            x = rect.get_x() + rect.get_width() / 2
            y = rect.get_y() + rect.get_height() / 2
            rotation = (90 + (360 - np.degrees(x) % 180)) % 360
            ax.text(x, y, label, ha='center', va='center', rotation=rotation, size='small', color='yellow')
    if level == 0:
        ax.set_theta_direction(-1)
        ax.set_theta_zero_location('N')
        ax.set_axis_off()

        plt.savefig("static/" + title + ".svg")
        plt.show()


if __name__ == '__main__':
    species_dict = {
        "homo sapiens": 5,
        "lasius niger": 6,
        "Griseotyrannus aurantioatrocristatus": 42,
        "boops boops": 8

    }
    create_piechart(species_dict, title="barplot")
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