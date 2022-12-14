# -*- coding:utf-8 -*-
# /usr/bin/env python
"""
Date: 2022/2/22 16:05
Desc: HTTP 模式主文件
"""
import json
import urllib.parse

import akshare as ak
from fastapi import APIRouter
from fastapi import status
from fastapi import Request
from fastapi.responses import JSONResponse


app_core = APIRouter()


@app_core.get("/public/{item_id}", description="公开接口", summary="该接口主要提供公开访问来获取数据")
def root(request: Request, item_id: str):
    """
    接收请求参数及接口名称并返回 JSON 数据
    此处由于 AKShare 的请求中是同步模式，所以这边在定义 root 函数中没有使用 asyncio 来定义，这样可以开启多线程访问
    :param request: 请求信息
    :type request: Request
    :param item_id: 必选参数; 测试接口名 stock_dxsyl_em 来获取 打新收益率 数据
    :type item_id: str
    :return: 指定 接口名称 和 参数 的数据
    :rtype: json
    """
    interface_list = dir(ak)
    decode_params = urllib.parse.unquote(str(request.query_params))
    # print(decode_params)
    if item_id not in interface_list:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "未找到该接口，请升级 AKShare 到最新版本并在文档中确认该接口的使用方式：https://www.akshare.xyz"
            },
        )
    if "cookie" in decode_params:
        eval_str = (
            decode_params.split("=", maxsplit=1)[0]
            + "='"
            + decode_params.split("=", maxsplit=1)[1]
            + "'"
        )
        eval_str = eval_str.replace("+", " ")
    else:
        eval_str = decode_params.replace("&", '", ').replace("=", '="') + '"'
        eval_str = eval_str.replace("+", " ")  # 处理传递的参数中带空格的情况
    if not bool(request.query_params):
        try:
            received_df = eval("ak." + item_id + f"()")
            if received_df is None:
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={"error": "该接口返回数据为空，请确认参数是否正确：https://www.akshare.xyz"},
                )
            temp_df = received_df.to_json(orient="records", date_format="iso")
        except KeyError as e:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "error": f"请输入正确的参数错误 {e}，请升级 AKShare 到最新版本并在文档中确认该接口的使用方式：https://www.akshare.xyz"
                },
            )
        return JSONResponse(status_code=status.HTTP_200_OK, content=json.loads(temp_df))
    else:
        try:
            received_df = eval("ak." + item_id + f"({eval_str})")
            if received_df is None:
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={"error": "该接口返回数据为空，请确认参数是否正确：https://www.akshare.xyz"},
                )
            temp_df = received_df.to_json(orient="records", date_format="iso")
        except KeyError as e:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "error": f"请输入正确的参数错误 {e}，请升级 AKShare 到最新版本并在文档中确认该接口的使用方式：https://www.akshare.xyz"
                },
            )
        return JSONResponse(status_code=status.HTTP_200_OK, content=json.loads(temp_df))
