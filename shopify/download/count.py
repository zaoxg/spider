import time


def countTime(func):
    start = time.time()
    func
    end = time.time()
    download = end - start
    print(f'下载耗时: {download}s')