<p align="center">
<img src="medias/main.jpeg" width=177 height=100 />
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

cd Sharingan

python3 -m pip install -r requirements.txt
```


# 案例用法

```sh
python3 worker.py blue

```

# 添加新站点

我有曾考虑过使用 `json` 作为站点的配置文件，但后来还是把它写在了 `extract.py`中

我们需要做的是在 `class Extractor` 下添加如下方法，其中 `upload` 方法中存放对应站点的基础配置

可选配置详见 [`models.py`](https://github.com/aoii103/Sharingan/blob/master/sharingan/models.py#L25)


```python

    @staticmethod
    def __example() -> Generator:
        """
            fs0c131y
            1. <-- yield your config first
            2. --> then got your datas back 
            3. <-- finally, yield the extracted data back
        """
        T = yield from upload(
            {
                "url": "http://xxxx", 
            }
        )

        T.name = T.html.pq('title').text()

        yield T

```


# TODO

- 格式化输出

# 📝 License

This project is [MIT](https://github.com/kefranabg/readme-md-generator/blob/master/LICENSE) licensed.

***

如果您觉得这个脚本对您有用，可别忘了star哟🐶。灵感来自 ❤️ [sherlock](https://github.com/sherlock-project/sherlock)
