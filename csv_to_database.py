import pandas as pd
from sqlalchemy import create_engine
import re

df = pd.read_csv('result.csv')
df['created_on'] = '2022-04-15'
df['douban_id'] = df['douban_url'].str.replace('https://movie.douban.com/subject/', '', regex=False).str.replace('/', '', regex=False)
print(df['douban_id'])
print(df)

# engine = create_engine('postgresql://scott:tiger@localhost:5432/mydatabase', echo=False)
