## bilibili数据分析爬虫
### 因变量（Y）
- [x] b站视频播放量
### 自变量（X）
- [x] 视频名称（与视频号码一一对应）
- [x] 上传时间
- [x] 视频类型
- [x] 视频标签
- [x] 视频获得的硬币量
- [x] 视频获得的收藏次数
- [x] 视频获得的分享次数
- [x] 视频时长
- [ ] up主（视频上传者）投稿数量
- [ ] up主（视频上传者）粉丝数。

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

    ```https://api.bilibili.com/x/tag/archive/tags?aid={}```
    * 获取aid所对应的所有标签
3. 直接访问页面
    * 视频名称（与视频号码一一对应）
    * 上传时间
    * 视频类型
    * 视频标签
    * 视频时长