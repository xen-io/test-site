#!/usr/bin/env python

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

with open('index.html') as f:
    root_html = f.read()
with open('page1.html') as f:
    page1_html = f.read()
with open('page2.html') as f:
    page2_html = f.read()


@app.get('/', response_class=HTMLResponse)
async def root():
    return root_html


@app.get('/page1', response_class=HTMLResponse)
async def page1():
    return page1_html


@app.get('/page2', response_class=HTMLResponse)
async def page2():
    return page2_html
