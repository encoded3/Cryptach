import zipfile
import json
import shutil
import random
import string
import os
from hashlib import sha256


params = {}

def _unpackProject(filepath: str) -> None:
    with zipfile.ZipFile(filepath, 'r') as zip_ref:
        os.mkdir("project")
        zip_ref.extractall("project/")

def _encrypt(text: str) -> str:
    m = sha256()
    m.update(text.encode())

    return m.hexdigest()
    
def _randomText(length: int) -> str:
    letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXY1234567890)(!@#$%^&{/"
    out = ""

    for i in range(length):
        out += random.choice(letters)

    return out

def _checkValue(value: str):
    return value in list(params.keys())
    
def _crBlock(block: dict) -> dict:
    if block["topLevel"]:
        block["x"] = random.randint(0, 1048576)
        block["y"] = random.randint(0, 1048576)

    return block

def _crSprite(sprite: dict) -> dict:
    if _checkValue("rename_variables"):
        for varname in list(sprite["variables"].keys()):
            sprite["variables"][varname][0] = _encrypt(sprite["variables"][varname][0])

    if _checkValue("extra_variables"):
        for i in range(256):
            sprite["variables"][_randomText(20)] = [
                _encrypt(_randomText(5)),
                _encrypt(_randomText(5))
            ]

            sprite["lists"][_randomText(20)] = [
                _encrypt(_randomText(5)),
                []
            ]

            sprite["broadcasts"][_randomText(20)] = _encrypt(_randomText(5))

    blocks = sprite["blocks"]

    if _checkValue("script_positions"):
        for i in blocks:
            sprite["blocks"][i] = _crBlock(blocks[i])

    if sprite["blocks"] != {} and _checkValue("extra_blocks"):
        for i in range(16):
            randIndex = random.choice(string.ascii_letters) + random.choice(string.ascii_letters)

            sprite["blocks"][_encrypt(randIndex)] = {
                                "opcode": random.choice([
                                    "control_repeat",
                                    "data_changevariableby",
                                    "procedures_definition",
                                    "event_whenflagclicked"
                                ]),
                                "next": None,
                                "parent": None,
                                "inputs": {},
                                "fields": {},
                                "shadow": False,
                                "topLevel": True,
                                "x": random.randint(0, 1048576),
                                "y": random.randint(0, 1048576)
                                }
            

    return sprite

def cryptach(parameters: dict) -> None:
    global params
    params=parameters

    params["ignore_sprites"] = params["ignore_sprites"].split(",")

    shutil.rmtree("project/")
    _unpackProject(params["file"])

    JSON = json.loads(open("project/project.json", "r").read())

    outTargets = []

    for sprite in JSON["targets"]:
        if not sprite["name"] in params["ignore_sprites"]: 
            sprite = _crSprite(sprite)
        
        outTargets.append(_crSprite(sprite))

    JSON["targets"] = outTargets

    JSON = json.dumps(JSON)
    open("project/project.json", "w").write(JSON)

    shutil.make_archive("output", "zip", "project/")
    os.rename("output.zip", "output.sb3")