from pandas import DataFrame, read_csv
import matplotlib.pyplot as plt
import pandas as pd

d = { 'name': ['Bob','Bart','Bobby'],
      'occupation': ['Lawyer','Programmer','Teacher']}

frame = pd.DataFrame(d, columns=['nam','occupatio'])
print(frame)
