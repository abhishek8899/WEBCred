from utils.databases import Genre_labels
from utils.essentials import Database

import matplotlib.pyplot as plt
import pandas as pd


database = Database(Genre_labels)
sample = database.getcolumndata('confidence')
data = []
for i in sample:
    data.append(i[0])
data = sorted(data)
data_dict = []
dp = pd.DataFrame(data)
dp.plot(kind='density')
plt.show()

# for i in sorted(set(data)):
#     data_dict += [i] * (len(data) - data.index(i))
#
# dp = pd.DataFrame(data_dict)
# dp.plot(kind='density')
# plt.show()
