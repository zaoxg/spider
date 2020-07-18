#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys

sys.path.append("./")
from settings import *
import os
import datetime

logger = {"test": None, }


def _log(file_path, platform, logging, RotatingFileHandler):
    """
    1.创建logger
    2.创建handler
    3.定义formatter
    4.给handler添加formatter
    5.给logger添加handler
    :param file_path: 日志路径
    :param platform: 日志文件名字
    :param logging:
    :param RotatingFileHandler:
    :return:
    """
    LOG_FILENAME = file_path + '/smallvideo.log'
    # 获取具有指定名称(通道名称)的日志记录器，并创建它
    logger[platform] = logging.getLogger(platform)
    # 设置日志等级
    logger[platform].setLevel(logging.DEBUG)
    # RotatingFileHandler 将日志记录到一组文件的处理程序，该处理程序将从一个文件切换到另一个文件当当前文件达到一定大小时，切换到下一个
    handler = RotatingFileHandler(LOG_FILENAME, encoding='UTF-8', maxBytes=1024 * 1024 * 100, backupCount=999)
    # 设置日志等级
    handler.setLevel(logging.DEBUG)
    # %(asctime)s字符串形式的当前时间。默认格式是 “2003-07-08 16:49:45,896”。逗号后面的是毫秒
    # %(levelname)s文本形式的日志级别
    # %(funcName)s调用日志输出函数的函数名
    # %(lineno)s调用日志输出函数的语句所在的代码行
    # %(message)s用户输出的消息
    # %(name)sLogger的名字
    # %(levelno)s数字形式的日志级别
    # %(pathname)s调用日志输出函数的模块的完整路径名，可能没有
    # %(filename)s调用日志输出函数的模块的文件名
    # %(module)s调用日志输出函数的模块名
    # %(created)f当前时间，用UNIX标准的表示时间的浮 点数表示
    # %(relativeCreated)d输出日志信息时的，自Logger创建以 来的毫秒数
    # %(thread)d线程ID。可能没有
    # %(threadName)s线程名。可能没有
    # %(process)d进程ID。可能没有
    # 日志的输出格式及方式做相关配置
    logging_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
    # 给handler添加formatter
    handler.setFormatter(logging_format)
    # 给logger添加handler
    logger[platform].addHandler(handler)


def myLogger(platform):
    import logging
    from logging.handlers import RotatingFileHandler

    file_name = datetime.datetime.now().strftime('%Y-%m-%d')
    pwd = os.getcwd()
    if SYSTEM_STATUS:
        # if "app" in pwd:
        #     c = pwd + "/logs/" + file_name
        # else:
        file_path = pwd + "/logs/" + platform + "/" + file_name
        # file_path = pwd+"/logs/" + file_name

    else:
        file_path = LOGPATH + "/smallvideo/" + platform + "/" + file_name

    # 没路径肯定没当前文件路径日志对象
    if not os.path.exists(file_path):
        os.makedirs(file_path)
        # 有路径有之前文件路径日志对象 删除
        if logger.get(platform, None):
            del logger[platform]
        # 有路径 有对象
        _log(file_path, platform, logging, RotatingFileHandler)
    # 有路径可能有日志对象
    else:
        # 没有对象 创建日志对象
        if not logger.get(platform, None):
            _log(file_path, platform, logging, RotatingFileHandler)
        # 有路径 有对象
    return logger[platform]


def logInfo(platform, content):
    try:
        myLogger(platform).info(content)
    except:
        myLogger(platform).info(content)


def logDebug(platform, cotent):
    try:
        myLogger(platform).debug(cotent)
    except:
        myLogger(platform).debug(cotent)


def logError(platform, content):
    try:
        myLogger(platform).error(content)
    except:
        myLogger(platform).error(content)
