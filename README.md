# pdd-crawl
This reposity is to crawl  commodity datas from website of pdd.

# 使用方法

## 一、驱动下载
需要下载一个浏览器和驱动
下载地址：https://googlechromelabs.github.io/chrome-for-testing/

进去之后点击stable
<img width="956" alt="image" src="https://github.com/BDW-o/pdd-crawl/assets/135718733/19b8b271-821f-42ec-a1ed-9f31fbd4e2dd">

选择对应版本的chrome和chrome_driver，我的是win64
<img width="959" alt="image" src="https://github.com/BDW-o/pdd-crawl/assets/135718733/e176221f-ab92-492b-b1ab-fdf70aad747e">

## 二、配置文件sets.yaml
注意要与代码放在与代码相同文件夹下
第一条是浏览器缓存路径，将用来保存历史记录，cookies等信息，可自行决定，没有的话会自动生成

第二条和第三条分别是浏览器驱动路径和浏览器路径
<img width="577" alt="image" src="https://github.com/BDW-o/pdd-crawl/assets/135718733/0d6b2f6c-916b-494c-9322-35a849af0346">

将之前下载好的浏览器和驱动路径放进去，注意驱动文件不带后缀名而浏览器文件需要
导入相应的包即可开始crawl

## 三、程序使用
成功运行文件后会打开浏览器并生成一个窗口
窗口上的按钮在此页面才可以使用
![image](https://github.com/BDW-o/pdd-crawl/assets/135718733/b8ab779f-d3af-43d5-98c6-f0c711359982)


首先输入需要抓取的商品个数，并点击爬取
出现商品信息预览
![image](https://github.com/BDW-o/pdd-crawl/assets/135718733/7c21b762-a0a9-4b14-92a9-f96572f9fa75)


确认无误后保存即可

