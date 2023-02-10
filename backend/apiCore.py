# Name: apiCore
# Author: Reacubeth
# Time: 2023/2/9 16:47
# Mail: noverfitting@gmail.com
# Site: www.omegaxyz.com
# *_*coding:utf-8 *_*


import uvicorn
from fastapi import FastAPI, Query, Form, APIRouter, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import time
import os
import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
import os
import re


GPU_ID = "0"
os.environ["CUDA_VISIBLE_DEVICES"] = GPU_ID

use_cuda = torch.cuda.is_available()
if use_cuda:
    print('***************GPU_ID***************: ', GPU_ID)
else:
    raise NotImplementedError

# Model Definition
t5_model_name = 't5-base'
tokenizer = T5Tokenizer.from_pretrained(t5_model_name)
kg_tokens_dict = ['<H>', '<R>', '<T>']
num_added_toks = tokenizer.add_tokens(kg_tokens_dict)
text_prefix = "TEXT: "
graph_prefix = "GRAPH: "

model = torch.load('webNLG_model.pkl')


app = FastAPI(
    docs_url='/api/v1/docs',
    redoc_url='/api/v1/redoc',
    openapi_url='/api/v1/openapi.json'
)

router = APIRouter()


def parse_triple(content):
    entity_ls = set([_e.strip() for _e in list(set(re.findall(r"\s*<H>([\s\w\.\/\-]+)[<$]*", content) +
                                                   re.findall(r"\s*<R>([\s\w\.\/\-]+)[<$]*", content)))])

    hrt_ls = set([(_r[0].strip(), _r[1].strip(), _r[2].strip())
                  for _r in re.findall(r"<H>([^<]+)<R>([^<]+)<T>([^<]+)", content)])
    return entity_ls, hrt_ls


def gen_json_response(hrt_ls):
    """
    {"graph": { "nodes": [ { "id": 1, "label": "Bob", "color": "#ffffff" }, { "id": 2, "label": "Alice", "color": "#ff7675" } ],
        "edges": [ { "from": 1, "to": 2, "label": "roommate" }, ] } }
    """
    graph = {"nodes": [], "edges": []}
    node_id = 0
    node_dict = {}
    for _h, _r, _t in hrt_ls:
        if _h not in node_dict:
            node_dict[_h] = node_id
            graph["nodes"].append({"id": node_id, "label": _h, "color": "#ffffff"})
            node_id += 1
        if _t not in node_dict:
            node_dict[_t] = node_id
            graph["nodes"].append({"id": node_id, "label": _t, "color": "#ffffff"})
            node_id += 1
        graph["edges"].append({"from": node_dict[_h], "to": node_dict[_t], "label": _r})
    return {"graph": graph}


@router.get('/get_graph')
async def get_graph(
        text: str = Query(..., description='a sentence', example=''),
):
    start = time.time()
    input_content = text
    prefix = text_prefix

    input_content_tmp = tokenizer(prefix + input_content, return_tensors='pt', padding='max_length', max_length=500)
    input_ids = input_content_tmp.input_ids.cuda()
    am = input_content_tmp.attention_mask.cuda()

    model_outputs = model.generate(input_ids=input_ids, attention_mask=am,
                                   num_beams=4, length_penalty=2.0, max_length=500)

    out_content = tokenizer.decode(model_outputs[0], skip_special_tokens=True)
    if '<H>' in out_content:
        entity_pool, hrt_pool = parse_triple(out_content)
        print('-----Graph-----')
        data = gen_json_response(hrt_pool)
    else:
        print(out_content)
        data = {"graph": {"nodes": [], "edges": []}}

    return {'time': time.time() - start, 'data': data}


app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == '__main__':
    uvicorn.run(app=app, host="127.0.0.1", port=8000, workers=1)

# pip install python-multipart
