import pandas as pd
import numpy as np

data = pd.DataFrame(np.random.rand(500, 1) * 10, columns=['a'])

print(data)
