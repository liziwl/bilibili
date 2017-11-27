# B站爬虫
## 本次bilibili数据分析所需要的数据
### 因变量（Y）
- [x] b站视频播放量
### 自变量（X）
- [x] 视频名称
- [x] 视频号码
- [x] 上传时间
- [x] 视频类型
- [x] 视频标签
- [x] 视频获得的硬币量
- [x] 视频获得的收藏次数
- [x] 视频获得的分享次数
- [x] 视频时长
- [x] up主（视频上传者）投稿数量
- [x] up主（视频上传者）粉丝数。

## 运行环境
* Python3
* PyCharm
    
### 第三方包
* lxml
    
## 调用的API
1. 基本信息

    ```http://api.bilibili.com/archive_stat/stat?aid={}```
    * 视频编号
    * 播放量
    * 弹幕数
    * 评论数
    * 收藏数
    * 硬币数
    * 分享数

2. tag信息

    ```http://api.bilibili.com/x/tag/archive/tags?aid={}```
    * 获取aid所对应的所有标签

3. 直接访问页面

    ```http://bilibili.com/video/av{}```
    * 视频名称
    * 上传时间
    * 视频类型
    * 视频标签
    * 视频时长
    
4. 获取UP信息

    1. ```http://api.bilibili.com/cardrich?mid=777536```
        * up名
        * 粉丝数
    2. ```http://api.bilibili.com/x/space/navnum?mid=1351379```
        * 上传数