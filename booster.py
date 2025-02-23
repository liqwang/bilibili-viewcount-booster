import sys
import threading
from time import sleep
from typing import Optional
from datetime import date, datetime, timedelta

import requests
from fake_useragent import UserAgent

# parameters
timeout = 3  # seconds for proxy connection timeout
thread_num = 75  # thread count for filtering active proxies
round_time = 305  # seconds for each round of view count boosting
update_pbar_count = 10  # update view count progress bar for every xx proxies
bv = sys.argv[1]  # video BV id
target = int(sys.argv[2])  # target view count

# statistics tracking parameters
successful_hits = 0  # count of successful proxy requests
initial_view_count = 0  # starting view count
last_view_count = 0  # view count from previous update

def time(seconds: int) -> str:
    if seconds < 60:
        return f'{seconds}s'
    else:
        return f'{int(seconds / 60)}min {seconds % 60}s'

def pbar(n: int, total: int, hits: Optional[int], view_increase: Optional[int]) -> str:
    progress = '━' * int(n / total * 50)
    blank = ' ' * (50 - len(progress))
    if hits is None or view_increase is None:
        return f'\r{n}/{total} {progress}{blank}'
    else:
        return f'\r{n}/{total} {progress}{blank} [Hits: {hits}, Views+: {view_increase}]'

# 1.get proxy
print()
day = date.today()
while True:  # search for the latest day with proxies
    day = day - timedelta(days=1)
    proxy_url = f'https://checkerproxy.net/api/archive/{day.strftime("%Y-%m-%d")}'
    print(f'getting proxies from {proxy_url} ...')
    proxies = requests.get(proxy_url).json()
    if len(proxies) > 0:
        total_proxies = [proxy['addr'] for proxy in proxies]
        print(f'successfully get {len(total_proxies)} proxies')
        break
    else:
        print(f'no proxy')

# 2.filter proxies by multi-threading
active_proxies = []
count = 0
def filter_proxys(proxies: 'list[str]') -> None:
    global count
    for proxy in proxies:
        count = count + 1
        try:
            requests.post('http://httpbin.org/post',
                          proxies={'http': 'http://'+proxy},
                          timeout=timeout)
            active_proxies.append(proxy)
        except:  # proxy connect timeout
            pass
        print(f'{pbar(count, len(total_proxies), hits=None, view_increase=None)} {100*count/len(total_proxies):.1f}%   ', end='')


start_filter_time = datetime.now()
print('\nfiltering active proxies using http://httpbin.org/post ...')
thread_proxy_num = len(total_proxies) // thread_num
threads = []
for i in range(thread_num):
    # calculate the start and end index of the proxies that this thread needs to process
    start = i * thread_proxy_num
    end = start + thread_proxy_num if i < (thread_num - 1) else None  # the last thread processes the remaining proxies
    thread = threading.Thread(target=filter_proxys, args=(total_proxies[start:end],))
    thread.start()
    threads.append(thread)
for thread in threads:
    thread.join()  # wait for all threads to finish
filter_cost_seconds = int((datetime.now()-start_filter_time).total_seconds())
print(f'\nsuccessfully filter {len(active_proxies)} active proxies using {time(filter_cost_seconds)}')

# 3.boost view count
print(f'\nstart boosting {bv} at {datetime.now().strftime("%H:%M:%S")}')
current = 0
info = {}  # Initialize info dictionary

# Get initial view count
try:
    info = requests.get(f'https://api.bilibili.com/x/web-interface/view?bvid={bv}',
                       headers={'User-Agent': UserAgent().random}).json()['data']
    initial_view_count = info['stat']['view']
    last_view_count = initial_view_count
    current = initial_view_count
    print(f'Initial view count: {initial_view_count}')
except Exception as e:
    print(f'Failed to get initial view count: {e}')

while True:
    reach_target = False
    start_time = datetime.now()
    
    # send POST click request for each proxy
    for i, proxy in enumerate(active_proxies):
        try:
            if i % update_pbar_count == 0:  # update progress bar
                print(f'{pbar(current, target, successful_hits, current - initial_view_count)} updating view count...', end='')
                info = (requests.get(f'https://api.bilibili.com/x/web-interface/view?bvid={bv}',
                                     headers={'User-Agent': UserAgent().random})
                        .json()['data'])
                current = info['stat']['view']
                if current >= target:
                    reach_target = True
                    print(f'{pbar(current, target, successful_hits, current - initial_view_count)} done                 ', end='')
                    break

            requests.post('http://api.bilibili.com/x/click-interface/click/web/h5',
                          proxies={'http': 'http://'+proxy},
                          headers={'User-Agent': UserAgent().random},
                          timeout=timeout,
                          data={
                              'aid': info['aid'],
                              'cid': info['cid'],
                              'bvid': bv,
                              'part': '1',
                              'mid': info['owner']['mid'],
                              'jsonp': 'jsonp',
                              'type': info['desc_v2'][0]['type'] if info['desc_v2'] else '1',
                              'sub_type': '0'
                          })
            successful_hits += 1
            print(f'{pbar(current, target, successful_hits, current - initial_view_count)} proxy({i+1}/{len(active_proxies)}) success   ', end='')
        except:  # proxy connect timeout
            print(f'{pbar(current, target, successful_hits, current - initial_view_count)} proxy({i+1}/{len(active_proxies)}) fail      ', end='')

    if reach_target:  # reach target view count
        break
    remain_seconds = int(round_time-(datetime.now()-start_time).total_seconds())
    if remain_seconds > 0:
        for second in reversed(range(remain_seconds)):
            print(f'{pbar(current, target, successful_hits, current - initial_view_count)} next round: {time(second)}          ', end='')
            sleep(1)

final_increase = current - initial_view_count
success_rate = (successful_hits / len(active_proxies)) * 100 if active_proxies else 0
print(f'\nFinish at {datetime.now().strftime("%H:%M:%S")}')
print(f'Statistics:')
print(f'- Initial views: {initial_view_count}')
print(f'- Final views: {current}')
print(f'- Total increase: {final_increase}')
print(f'- Successful hits: {successful_hits}')
print(f'- Success rate: {success_rate:.2f}%\n')
