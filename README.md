# 简单网络巡检工具

## 概括

![](./static/image/image-20230311173710167.png)

该应用实现对交付工程师在交付交付中无相应网管设备，或者中小型网络运维无网管设备，需要对交换机设备做批量的信息收集而开发的一个可扩展性的网络设备信息收集工具。

工具特点：可以很便捷的扩展需要的功能，不需要去关注怎么连接设备问题，怎么处理数据问题，只需要在模板中添加对应模板，跟对应的收集数据函数就可以完成功能的扩展，可以适用于更多场景。

本项目做为开源项目，欢迎各位大拿多多出注意，有能力的可以一起对项目进行维护和修复BUG，一起成为开源社区中的一个贡献者。

**欢迎各位大佬入群交流和提交PR，或者提出需求，在能力范围内能满足的尽量满足，以及沟通成长，QQ群号：792637284**

### 部署文档

部署文档：[安装说明文档](.\docs\安装说明.md)

### 更新文档

版本更新文档：[更新说明文档](.\docs\更新说明.md)

### 应用介绍

应用介绍文档：[更新说明文档](.\docs\应用介绍.md)

### 前端源码

前端源码链接：https://github.com/liuyuanchengweb/simple_network_inspection_tool_vue3




## 快速部署

### 环境

Python 3.10以上

部署测试虚拟机为Windows10

![image-20230311183240998](./static/image/image-20230311183240998.png)

### 部署命令

~~~sh
# 查看自己环境的python版本
C:\Users\ycll>python -v
# 3.10以上
# 更新pip
C:\Users\ycll>python.exe -m pip install --upgrade pip
# 安装pipx
C:\Users\ycll>python -m pip install --user pipx -i https://pypi.tuna.tsinghua.edu.cn/simple
# pipx刷新到系统变量中
C:\Users\ycll>python -m pipx ensurepath
# 确认pipx安装是否正常
C:\Users\ycll>pipx --version
1.1.0
# 安装poetry会稍微有点慢
C:\Users\ycll>pipx install poetry -i https://pypi.tuna.tsinghua.edu.cn/simple
# 安装好确认安装正常
C:\Users\ycll>poetry -V
Poetry (version 1.4.0)
# 进入项目目录
C:\Users\ycll>cd C:\Users\ycll\Desktop\simple_network_inspection_tool_v0.2.0
# 安装依赖
C:\Users\ycll\Desktop\simple_network_inspection_tool_v0.2.0>poetry install
# 运行项目
poetry run run.py
~~~

![image-20230311184148620](./static/image/image-20230311184148620.png)

![image-20230311184946946](./static/image/image-20230311184946946.png)

默认监控18888端口

运行后访问127.0.0.1:18888为前端页面

接口文档地址为127.0.0.1:18888/docs

可以通过本地访问，也可以通过远端访问

![image-20230311185329838](./static/image/image-20230311185329838.png)

![image-20230311185357072](./static/image/image-20230311185357072.png)

## 感谢
前端室友
NetDevOps同路人：王印老师，九净老师，点滴技术，朱嘉盛老师

以及Netmiko开源项目，FastAPI,以及相关的开源项目
## 开源许可
开源许可遵循MIT开源协议
