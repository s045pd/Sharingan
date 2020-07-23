<p align="center">
<img src="medias/main.gif"/>
    <h1 align="center" >Sharingan</h1>
    <p align="center">我们将尽可能得从社交媒体中寻找您的基本可见足迹</p>
        <p align="center">
    <a href="https://app.codacy.com/manual/aoii103/Sharingan?utm_source=github.com&utm_medium=referral&utm_content=aoii103/Sharingan&utm_campaign=Badge_Grade_Dashboard"><img src="https://api.codacy.com/project/badge/Grade/f00d1d69a99346038d14df4bec303034"/></a>
    <a target="_blank" href="https://www.python.org/downloads/" title="Python version"><img src="https://img.shields.io/badge/python-%3E=_3.8-green.svg"></a>
    <a target="_blank" href="LICENSE" title="License: MIT"><img src="https://img.shields.io/badge/License-MIT-blue.svg"></a>
</p>




# 环境安装

首先保证您已经安装了```python3.8```及以上版本,然后依次运行如下命令。

```sh
git clone https://github.com/aoii103/Sharingan.git

cd sharingan

python3 setup.py install 
```

或通过pip安装

```bash
pip install sharingan
```



# 案例用法

```sh

cd sharingan

python3 -m sharingan blue

```

![](./medias/use.gif)

# 添加新站点

我有曾考虑过使用 `json` 作为站点的配置文件，但后来还是把它写在了 `extract.py`中

我们需要做的是在 `class Extractor` 下添加如下方法，其中 `upload` 方法中存放对应站点的基础配置

可选配置详见 [`models.py`](https://github.com/aoii103/Sharingan/blob/master/sharingan/models.py#L25)


```python

    @staticmethod
    def __example() -> Generator:
        """
            1. <-- yield your config first
            2. --> then got your datas back 
            3. <-- finally, yield the extracted data back
        """
        T = yield from upload(
            **{
                "url": "http://xxxx", 
            }
        )

        T.name = T.html.pq('title').text()
        ...

        yield T

```

# 单项测试

偶尔我们在编写添加新站点后需要进行测试

就可以用到如下代码，例如我们要测试 `twitter`

```bash

python3 -m sharingan larry --singel=twitter

```

# 通过 sherlock 创建站点

首先我们运行如下代码

```bash
python3 -m sharingan.common
```

然后它将创建一个叫`templates.py`的python脚本

我们将其中的代码替换到 `extract.py`的相应位置即可


# 选项

```bash

Usage: __main__.py [OPTIONS] NAME

Options:
  --name TEXT        您所需要搜索的用户名
  --proxy_uri TEXT   在需要翻墙是所使用的代理地址
  --no_proxy         所有的请求将进行直连
  --save_path TEXT   结果保留路径
  --pass_history     跳过历史保存结果，文件保存将标记时间戳
  --singel TEXT      在对单个目标进行爬行的时候使用
  --debug            开发者模式
  --update           将以更新的方式写入原有文件
  --workers INTEGER  异步worker数量
  --help             打印帮助文档 

```


# TODO

- 格式化输出

# 📝 License

This project is [MIT](https://github.com/kefranabg/readme-md-generator/blob/master/LICENSE) licensed.

***

如果您觉得这个脚本对您有用，可别忘了star哟🐶。灵感来自 ❤️ [sherlock](https://github.com/sherlock-project/sherlock)
