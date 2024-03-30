使用[代理池](https://checkerproxy.net/getAllProxy)对目标视频进行轮询点击，视作游客观看，速度约为8播放量/分钟

B站目前限制同一IP对视频点击间隔大于5min，所以代理轮询完后如果不足5min会继续等待

<br>

## 使用方法
#### 有Python环境
```shell
> git clone https://github.com/QuanQuan-CHO/bilibili-viewcount-booster.git
> cd bilibili-viewcount-booster
> pip install -r requirements.txt
> python booster.py <BV号> <目标播放数>
```

#### 无Python环境
1. 在[Release界面](https://github.com/QuanQuan-CHO/bilibili-viewcount-booster/releases/latest)下载与系统对应的文件
2. 重命名为`booster`(Windows为`booster.exe`)
3. 在终端中进入所在目录
```shell
> chmod +x booster (macOS/Linux的额外步骤)
> ./booster <BV号> <目标播放数>
```
> [!NOTE]
> macOS可能会遇到「无法打开"booster"，因为Apple无法检查其是否包含恶意软件」的报错，[参考解决方式](https://support.apple.com/zh-cn/guide/mac-help/mchleab3a043/mac)

<br>

## 运行效果
```
> ./booster BV1fz421o8J7 349

getting proxies from https://checkerproxy.net/api/archive/2024-03-29 ...
successfully get 2624 proxies

filtering active proxies using http://httpbin.org/post ...
2624/2624 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100.0%   
successfully filter 165 active proxies using 4min 36s

start boosting BV1fz421o8J7 at 20:27:40
361/349 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ done                    
finish at 20:33:04
```

<br>

## 参考
https://github.com/xu0329/bilibili_proxy
  
