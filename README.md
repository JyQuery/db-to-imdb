# douban-to-imdb
导出豆瓣电影评分到IMDB，进而导入Trakt.

## 需求

* [pyenv](https://github.com/pyenv/pyenv)
* [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv)

## 初始化

    $ pyenv install 3.8.0
    $ pyenv virtualenv 3.8.0 douban-to-imdb-env
    $ pyenv activate douban-to-imdb-env
    $ pip install -r requirements.txt
    
###### *・如果不使用虚拟环境，请参照requirements.txt中的内容自行安装*
    
## 使用

#### 导出豆瓣电影评分到CSV文件

    $ python douban_to_csv.py [user_id]
    
*其中`[user_id]`为豆瓣的用户 ID，查找方法参见：[如何查找自己的豆瓣 ID](https://github.com/pyenv/pyenv-virtualenv)*

#### 导入电影评分到IMDB

&ensp;&ensp;&ensp;&ensp;由于导入IMDB需要登录，所以此过程需要打开浏览器，等待自行登录IMDB账号。登录成功后浏览器会自动查找电影并进行打分，这是正常的程序操作，并不是闹鬼，请勿惊慌。 👻👻👻

    $ python csv_to_imdb.py [unmark/-2/-1/0/1/2]
    
###### *・参数如果为 unmark时，则会清除CSV文件中电影对应的 IMDB中的评分*

###### *・参数如果为数字时，则打分时分调传入的数值，范围为 ±2分*

###### *・参数为空时，默认打分 -1分（由于豆瓣打分粒度太大，导致本人评分标准往往会比实际稍高 1分左右）*

###### *例：（无参数）*
  
###### *&ensp;&ensp;&ensp;豆瓣评五星：IMDB打 9分 （考虑到实际是能满分的电影比较少）*
  
###### *&ensp;&ensp;&ensp;豆瓣评一星：IMDB打 1分 （考虑到你既然都打一星了肯定是这电影烂到你恨不得给 0分）*

## 运行截图

#### 导出CSV

&ensp;&ensp;&ensp;&ensp;我也是写这个程序的时候才发现，一些包含情色或者暴力内容的电影，在不登录豆瓣账号的情况下打开对应条目会显示访问的页面不存在，如：罗马帝国艳情史，树大招风等，这些条目请自行手工标记打分。还有就是一些条目在豆瓣的条目页里没有对应的IMDB条目，应该是本来在IMDB的数据库中就没有，如：极限挑战第五季等，这种条目就没有办法了。

![image](https://github.com/fisheepx/douban-to-imdb/blob/master/screenshots/douban-to-csv1.png)

![image](https://github.com/fisheepx/douban-to-imdb/blob/master/screenshots/douban-to-csv2.png)

#### 导入IMDB

![image](https://github.com/fisheepx/douban-to-imdb/blob/master/screenshots/csv-to-imdb2.png)

![image](https://github.com/fisheepx/douban-to-imdb/blob/master/screenshots/csv-to-imdb1.png)

## 关于

* #### 如何查找自己的豆瓣ID

&ensp;&ensp;&ensp;&ensp; 先登录自己的豆瓣账号，然后点击右上角的名字，打开[个人主页](https://www.douban.com/mine/)，就在跳转到的URL里：https://www.douban.com/people/[这里的数字就是你的user_id]/
