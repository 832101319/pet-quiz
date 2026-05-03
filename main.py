from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Optional
import json
import os

app = FastAPI(title="魔法生物商店 · 斯莱特林")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 魔法生物列表
CREATURES = [
    "雪鸮", "大灰鸮", "小鸮", "雕鸮", "鸣角鸮", "仓鸮", "灰林鸮", "草鸮",
    "猫", "蟾蜍", "老鼠", "侏儒蒲", "护树罗锅", "猫狸子", "嗅嗅",
    "双头水螈", "蒲绒绒", "绝音鸟", "恶婆鸟", "弗洛伯毛虫", "土扒貂"
]

# 题目数据
QUESTIONS = [
    {
        "id": 1,
        "part": "第一部分 · 初见",
        "text": "你推开店门时，余光注意到柜台后面有什么东西在动。它是：",
        "options": [
            {"label": "A", "text": "一团毛茸茸的褐色圆球，正在翻你的钱袋子", "scores": {"嗅嗅": 2, "猫狸子": 1}},
            {"label": "B", "text": "一只蹲在账本上的猫头鹰，歪头盯着你", "scores": {"雪鸮": 2, "大灰鸮": 1}},
            {"label": "C", "text": "一条……尾巴？银白色的，从货架后面无声无息滑过去", "scores": {"双头水螈": 2, "猫": 1}},
            {"label": "D", "text": "柜台上有一只扁扁的、看着像棕色橡皮泥的生物", "scores": {"弗洛伯毛虫": 2, "蒲绒绒": 1}},
        ]
    },
    {
        "id": 2,
        "part": "第一部分 · 初见",
        "text": "店里有一股说不出的气味。你闻到的是：",
        "options": [
            {"label": "A", "text": "旧羊皮纸 + 薄荷", "scores": {"_all_owls": 1}},
            {"label": "B", "text": "湿木头 + 蘑菇", "scores": {"护树罗锅": 2, "绝音鸟": 1}},
            {"label": "C", "text": "肉桂 + 一点点……铁锈味？", "scores": {"猫狸子": 2, "猫": 1}},
            {"label": "D", "text": "说不上来，但你觉得很安全，像个窝", "scores": {"蒲绒绒": 2, "侏儒蒲": 1}},
        ]
    },
    {
        "id": 3,
        "part": "第二部分 · 白昼与黑夜",
        "text": "如果让你选一个词形容喜欢的光：",
        "options": [
            {"label": "A", "text": "太阳光", "scores": {"_non_owls": 1}},
            {"label": "B", "text": "月光", "scores": {"雕鸮": 2, "大灰鸮": 2, "鸣角鸮": 2, "仓鸮": 2, "猫": 2, "双头水螈": 1}},
            {"label": "C", "text": "烛光", "scores": {"仓鸮": 1, "灰林鸮": 1, "猫狸子": 1, "土扒貂": 1}},
            {"label": "D", "text": "没有光", "scores": {"蟾蜍": 2, "_all_bugs": 2, "猫": 1}},
        ]
    },
    {
        "id": 4,
        "part": "第二部分 · 白昼与黑夜",
        "text": "半夜你在宿舍被一种声音吵醒。那是：",
        "options": [
            {"label": "A", "text": "轻轻的咕——咕——", "scores": {"灰林鸮": 2, "鸣角鸮": 2}},
            {"label": "B", "text": "持续的低吟，像风穿过石头的声音", "scores": {"双头水螈": 2, "绝音鸟": 1}},
            {"label": "C", "text": "啪的一声——不是老鼠，是更小的、软软的脚步声", "scores": {"侏儒蒲": 2, "蒲绒绒": 1, "弗洛伯毛虫": 1}},
            {"label": "D", "text": "很远处一声高高的呼——", "scores": {"雕鸮": 2, "大灰鸮": 1}},
            {"label": "E", "text": "什么声音都没有。但你知道有什么东西在看着你", "scores": {"猫狸子": 2, "猫": 1, "护树罗锅": 1}},
        ]
    },
    {
        "id": 5,
        "part": "第二部分 · 白昼与黑夜",
        "text": "你更喜欢：",
        "options": [
            {"label": "A", "text": "打开窗帘睡觉", "scores": {"雪鸮": 2, "草鸮": 2, "大灰鸮": 1, "鸣角鸮": 1}},
            {"label": "B", "text": "拉紧窗帘", "scores": {"雕鸮": 2, "仓鸮": 2, "灰林鸮": 2, "猫": 2, "蟾蜍": 1, "双头水螈": 1}},
            {"label": "C", "text": "无所谓，但是要有一个软的地方靠着", "scores": {"蒲绒绒": 2, "侏儒蒲": 1, "猫": 1}},
        ]
    },
    {
        "id": 6,
        "part": "第三部分 · 温度与手掌",
        "text": "你的手现在是：",
        "options": [
            {"label": "A", "text": "偏凉", "scores": {"_all_owls": 1, "双头水螈": 1, "蟾蜍": 1}},
            {"label": "B", "text": "偏暖", "scores": {"蒲绒绒": 2, "侏儒蒲": 1, "猫狸子": 1, "猫": 1}},
            {"label": "C", "text": "说不准", "scores": {"_all_reptiles": 1}},
        ]
    },
    {
        "id": 7,
        "part": "第三部分 · 温度与手掌",
        "text": "如果让你养一只会碰到你的宠物，你更接受：",
        "options": [
            {"label": "A", "text": "每天落在你肩上", "scores": {"雪鸮": 2, "大灰鸮": 2}},
            {"label": "B", "text": "偶尔蹲在你膝盖上", "scores": {"猫狸子": 2, "侏儒蒲": 1}},
            {"label": "C", "text": "藏在你的袍子口袋里", "scores": {"嗅嗅": 2, "蒲绒绒": 2, "侏儒蒲": 1}},
            {"label": "D", "text": "请不要碰我", "scores": {"蟾蜍": 2, "弗洛伯毛虫": 2, "老鼠": 1}},
        ]
    },
    {
        "id": 8,
        "part": "第三部分 · 温度与手掌",
        "text": "你对湿冷的东西：",
        "options": [
            {"label": "A", "text": "完全不介意", "scores": {"双头水螈": 3, "蟾蜍": 2, "弗洛伯毛虫": 1}},
            {"label": "B", "text": "有点介意", "scores": {"_all_feather": 1, "_all_mammal": 1}},
            {"label": "C", "text": "不能忍", "scores": {"双头水螈": -3, "蟾蜍": -2, "弗洛伯毛虫": -1}},
        ]
    },
    {
        "id": 9,
        "part": "第四部分 · 安静与吵闹",
        "text": "你在公共休息室最喜欢的位置是：",
        "options": [
            {"label": "A", "text": "壁炉旁边", "scores": {"蒲绒绒": 2, "猫狸子": 1, "侏儒蒲": 1}},
            {"label": "B", "text": "窗边", "scores": {"_all_owls": 2}},
            {"label": "C", "text": "角落、黑暗一点的地方", "scores": {"灰林鸮": 2, "仓鸮": 2, "猫": 2, "双头水螈": 1}},
            {"label": "D", "text": "不固定", "scores": {"老鼠": 2, "土扒貂": 1}},
        ]
    },
    {
        "id": 10,
        "part": "第四部分 · 安静与吵闹",
        "text": "你对突然的大声音的反应是：",
        "options": [
            {"label": "A", "text": "被吓一跳，但很快恢复", "scores": {"_all_birds": 2, "猫狸子": 1}},
            {"label": "B", "text": "几乎没反应", "scores": {"蟾蜍": 2, "弗洛伯毛虫": 1, "双头水螈": 1}},
            {"label": "C", "text": "会后退一下", "scores": {"蒲绒绒": 2, "侏儒蒲": 1, "老鼠": 1}},
            {"label": "D", "text": "本能压低身体，静止不动", "scores": {"猫": 2, "护树罗锅": 1, "土扒貂": 1}},
        ]
    },
    {
        "id": 11,
        "part": "第四部分 · 安静与吵闹",
        "text": "别人在宿舍大声聊天时，你的宠物应该：",
        "options": [
            {"label": "A", "text": "跟着一起参与", "scores": {"雪鸮": 2, "大灰鸮": 1}},
            {"label": "B", "text": "安静待着", "scores": {"绝音鸟": 2, "弗洛伯毛虫": 1, "蟾蜍": 1}},
            {"label": "C", "text": "躲到你床底下", "scores": {"护树罗锅": 2, "猫狸子": 1}},
            {"label": "D", "text": "完全不搭理，做自己的事", "scores": {"猫": 2, "老鼠": 1, "双头水螈": 1}},
        ]
    },
    {
        "id": 12,
        "part": "第五部分 · 规则与边界",
        "text": "以下哪一种行为你最不能接受：",
        "options": [
            {"label": "A", "text": "偷你的零食", "scores": {"嗅嗅": 2, "老鼠": 1}},
            {"label": "B", "text": "把你的衣服咬一个洞", "scores": {"嗅嗅": 2, "护树罗锅": 1}},
            {"label": "C", "text": "半夜在宿舍里跑", "scores": {"老鼠": 2, "侏儒蒲": 1, "猫": 1}},
            {"label": "D", "text": "随地……你知道的", "scores": {}},
        ]
    },
    {
        "id": 13,
        "part": "第五部分 · 规则与边界",
        "text": "如果宠物不听话，你会：",
        "options": [
            {"label": "A", "text": "耐心教", "scores": {"猫狸子": 2, "猫": 2, "护树罗锅": 2, "雪鸮": 1}},
            {"label": "B", "text": "算了，它开心就好", "scores": {"蒲绒绒": 2, "弗洛伯毛虫": 1, "蟾蜍": 1}},
            {"label": "C", "text": "试着找到它不想听话的原因", "scores": {"嗅嗅": 2, "猫": 2, "大灰鸮": 1}},
            {"label": "D", "text": "不会发生，因为我不会选一个我不了解的宠物", "scores": {"_smart": 1}},
        ]
    },
    {
        "id": 14,
        "part": "第五部分 · 规则与边界",
        "text": "你更愿意你的宠物：",
        "options": [
            {"label": "A", "text": "被很多人喜欢", "scores": {"雪鸮": 2, "蒲绒绒": 2, "侏儒蒲": 1}},
            {"label": "B", "text": "只亲近你一个人", "scores": {"大灰鸮": 2, "雕鸮": 2, "猫狸子": 2, "猫": 2}},
            {"label": "C", "text": "无所谓，它健康就行", "scores": {"_all": 1}},
        ]
    },
    {
        "id": 15,
        "part": "第六部分 · 秘密与细微",
        "text": "你相信动物能知道你的情绪吗：",
        "options": [
            {"label": "A", "text": "相信，而且我需要这样的能力", "scores": {"猫狸子": 2, "猫": 2, "护树罗锅": 2}},
            {"label": "B", "text": "相信，但不强求", "scores": {"_all_owls": 1, "蒲绒绒": 1}},
            {"label": "C", "text": "不太信", "scores": {"蟾蜍": 2, "弗洛伯毛虫": 1}},
        ]
    },
    {
        "id": 16,
        "part": "第六部分 · 秘密与细微",
        "text": "你在深夜会做以下哪件事：",
        "options": [
            {"label": "A", "text": "写日记", "scores": {"灰林鸮": 2, "仓鸮": 2}},
            {"label": "B", "text": "看书", "scores": {"_all_owls": 2}},
            {"label": "C", "text": "发呆", "scores": {"猫": 2, "绝音鸟": 1, "双头水螈": 1}},
            {"label": "D", "text": "偷偷吃零食", "scores": {"嗅嗅": 2, "老鼠": 1, "侏儒蒲": 1}},
        ]
    },
    {
        "id": 17,
        "part": "第六部分 · 秘密与细微",
        "text": "如果你要给你的宠物取个名字，你会偏向：",
        "options": [
            {"label": "A", "text": "一个古老的名字", "scores": {"雕鸮": 2, "大灰鸮": 2, "猫狸子": 1}},
            {"label": "B", "text": "一个可爱简单的名字", "scores": {"蒲绒绒": 2, "侏儒蒲": 2, "雪鸮": 1}},
            {"label": "C", "text": "一个很奇怪、别人听不懂的名字", "scores": {"护树罗锅": 2, "双头水螈": 1, "绝音鸟": 1}},
            {"label": "D", "text": "不取名字，它不需要被命名", "scores": {"猫": 2, "蟾蜍": 1}},
        ]
    },
    {
        "id": 18,
        "part": "第七部分 · 边界与底线",
        "text": "你对虫子的态度是：",
        "options": [
            {"label": "A", "text": "还好", "scores": {"弗洛伯毛虫": 2, "绝音鸟": 1, "土扒貂": 1}},
            {"label": "B", "text": "太恶心了不行", "scores": {"弗洛伯毛虫": -3, "双头水螈": -2, "土扒貂": -2}},
            {"label": "C", "text": "无所谓但不想碰", "scores": {"_all_feather": 1, "_all_mammal": 1}},
        ]
    },
    {
        "id": 19,
        "part": "第七部分 · 边界与底线",
        "text": "你对老鼠的态度是：",
        "options": [
            {"label": "A", "text": "可爱", "scores": {"老鼠": 3, "猫狸子": 1}},
            {"label": "B", "text": "害怕", "scores": {"老鼠": -3, "猫": -2}},
            {"label": "C", "text": "没什么感觉", "scores": {"猫": 1, "土扒貂": 1}},
        ]
    },
    {
        "id": 20,
        "part": "第七部分 · 边界与底线",
        "text": "你对夜晚活动的宠物：",
        "options": [
            {"label": "A", "text": "完全可以，我睡得晚", "scores": {"雕鸮": 2, "仓鸮": 2, "灰林鸮": 2, "猫": 2, "双头水螈": 1, "蟾蜍": 1}},
            {"label": "B", "text": "不太行，我需要安静睡觉", "scores": {"雪鸮": 2, "草鸮": 2, "蒲绒绒": 1, "侏儒蒲": 1}},
        ]
    },
    {
        "id": 21,
        "part": "第八部分 · 最后三题",
        "text": "你小时候，有没有盯着一个东西看过很久——久到它好像不再是它了？那是什么颜色？",
        "options": [],
        "free_text": True,
        "note": "此题不计分，仅用于丰富场景描述"
    },
    {
        "id": 22,
        "part": "第八部分 · 最后三题",
        "text": "你觉得自己更像：",
        "options": [
            {"label": "A", "text": "树", "scores": {"护树罗锅": 2, "绝音鸟": 1, "灰林鸮": 1}},
            {"label": "B", "text": "风", "scores": {"雪鸮": 2, "草鸮": 2, "鸣角鸮": 1}},
            {"label": "C", "text": "石头", "scores": {"雕鸮": 2, "猫狸子": 1, "蟾蜍": 1}},
            {"label": "D", "text": "水", "scores": {"双头水螈": 2, "猫": 1, "老鼠": 1}},
        ]
    },
    {
        "id": 23,
        "part": "第八部分 · 最后三题",
        "text": "你走进店的最后一刻，听到柜台后面有人说了一句：有的魔法生物一辈子只效忠于一名巫师。你心里想的是：",
        "options": [
            {"label": "A", "text": "太好了", "scores": {"猫狸子": 2, "猫": 2, "护树罗锅": 2}},
            {"label": "B", "text": "压力好大", "scores": {"雪鸮": 2, "蒲绒绒": 2, "侏儒蒲": 1}},
            {"label": "C", "text": "真的假的", "scores": {"嗅嗅": 2, "大灰鸮": 1, "老鼠": 1}},
            {"label": "D", "text": "我不想被它绑住", "scores": {"_all_owls": 1, "_loyal": -1}},
        ]
    },
    {
        "id": 24,
        "part": "第八部分 · 最后三题",
        "text": "最后一道题。它对你说：就是你了，小巫师。你第一反应想对它说的是：",
        "options": [
            {"label": "A", "text": "我会照顾好你。", "scores": {"_loyal": 2}},
            {"label": "B", "text": "你要乖哦。", "scores": {"蒲绒绒": 2, "侏儒蒲": 2, "弗洛伯毛虫": 1}},
            {"label": "C", "text": "你可别惹事。", "scores": {"嗅嗅": 2, "猫狸子": 2, "猫": 1}},
            {"label": "D", "text": "那我们互相适应吧。", "scores": {"_smart": 2}},
        ]
    },
]

# 忌讳问卷
TABOO_QUESTION = {
    "id": 99,
    "part": "忌讳问卷 · 最后的问话",
    "text": "他手肘撑在柜台上，推给你一张纸，上面只写了一行字：你最不愿意醒来的梦里，出现了什么？",
    "options": [
        {"label": "A", "text": "湿湿的、软软的东西从你手背上爬过去", "effect": "弗洛伯毛虫,双头水螈,土扒貂"},
        {"label": "B", "text": "黑暗里有细碎的脚步声，不止一对", "effect": "老鼠,猫"},
        {"label": "C", "text": "明明安静得很，你却浑身发毛", "effect": "绝音鸟,护树罗锅"},
        {"label": "D", "text": "什么都没有发生。但你就是睡不着", "effect": "none"},
    ]
}

# 特殊标签映射
OWL_CREATURES = ["雪鸮", "大灰鸮", "小鸮", "雕鸮", "鸣角鸮", "仓鸮", "灰林鸮", "草鸮"]
BUG_CREATURES = ["弗洛伯毛虫"]
REPTILE_CREATURES = ["双头水螈", "蟾蜍"]
BIRD_CREATURES = ["雪鸮", "大灰鸮", "小鸮", "雕鸮", "鸣角鸮", "仓鸮", "灰林鸮", "草鸮", "绝音鸟", "恶婆鸟"]
FEATHER_CREATURES = ["雪鸮", "大灰鸮", "小鸮", "雕鸮", "鸣角鸮", "仓鸮", "灰林鸮", "草鸮", "绝音鸟", "恶婆鸟"]
MAMMAL_CREATURES = ["猫", "老鼠", "侏儒蒲", "猫狸子", "嗅嗅", "蒲绒绒", "土扒貂"]
LOYAL_CREATURES = ["猫狸子", "猫", "护树罗锅", "大灰鸮", "雕鸮"]
SMART_CREATURES = ["猫狸子", "猫", "护树罗锅", "嗅嗅", "大灰鸮"]

# 走出画面文案
SCENES = {
    "雪鸮": "最先动的是横梁。\n\n一片白色从高处落下来，没有声音，像一小团云掉进了房间里。\n\n它落在桌角，歪头看你。\n\n翅膀收拢的时候，带起一阵很淡的凉风——不是冷，是北边的气息。\n\n雪鸮眨了眨眼，金色的瞳仁里映出你的影子。\n\n它很少主动靠近人。店员的声音从你身后传来，但它看了你很久了。\n\n那只雪鸮没有叫。它只是静静地站在那里，像一封还没拆开的信。",

    "大灰鸮": "你没有看见它从哪里出来的。\n\n它已经站在窗台上了。\n\n大灰鸮的羽毛是银灰色的，像旧月光凝成了固体。它没有歪头，没有眨眼，只是直直地看着你。\n\n那种注视不是好奇。\n\n是辨认。\n\n店员轻轻嗯了一声。\n\n大灰鸮突然展开翅膀——巨大、无声——然后收拢，重新变成一尊灰色的雕像。\n\n它没有飞向你。\n\n但它也没飞走。",

    "小鸮": "你先是感觉到有什么东西轻轻擦过了你的耳朵。\n\n很轻。像风吹过一根头发。\n\n然后你低头——\n\n一只巴掌大的小鸮站在你的膝盖上，仰头看你。\n\n它太小了。小到你怕呼吸重一点，它就会被吹走。\n\n但它不怕你。\n\n它甚至往前跳了一步，更靠近你的手。\n\n它不轻易停在人身上。店员的声音有点意外，它停过的人……都没让它失望过。",

    "雕鸮": "你听到了一声极低的呼——，像是从墙里面传出来的。\n\n然后整个柜台颤了一下。\n\n雕鸮落下来的时候，你才意识到它有多大。翅膀展开像一件斗篷，收起来之后，它仍然占据了半张桌子。\n\n它没有看你。\n\n它看着店员。店员点了一下头，它才转过头来看你。\n\n那目光沉沉的，像一口老钟。\n\n它在等你说一句话。店员说，什么都可以。",

    "鸣角鸮": "你听到了声音，才看见它。\n\n不是叫声——是翅膀。它飞的时候，空气里有什么东西在轻轻震响，像有人用指尖弹了一下水晶杯。\n\n鸣角鸮落在烛台旁边，月光刚好照到它的脸。\n\n它看了你一眼，然后轻轻叫了一声。\n\n呜——\n\n很短。\n\n像试探，像打招呼，像在说我在这里。\n\n店员笑了一下。它平时不怎么出声。今天倒是大方。",

    "仓鸮": "它从暗处走出来。\n\n不是飞。是走。\n\n仓鸮走路的样子有点笨拙，一摇一摆的，像个还没学会跑步的小孩。\n\n它的脸是心形的。在烛光下看，那双黑眼睛显得格外大。\n\n它走到你脚边，停下来，仰头看你。\n\n没有声音。没有动作。\n\n只是站着。\n\n……它选你了。店员的声音低下去，它很少选人。它害羞。",

    "灰林鸮": "你以为店里没有其他生物了。\n\n然后你余光扫到书架的第二层——一团灰褐色的东西动了。\n\n灰林鸮把自己藏得很好。它睁开眼的时候，你才发现那不是一块树皮，是一张脸。\n\n它没有飞下来。就蹲在那里，看着你。\n\n店员抬头看了它一眼：它不下来。但它愿意让你看见它。\n\n对灰林鸮来说，这已经是很大的信任了。",

    "草鸮": "窗户不知道什么时候被推开了一条缝。\n\n你回头的时候，草鸮已经站在窗框上了。\n\n它通体浅金，像被月光洗褪了颜色的麦田。翅膀边缘有很淡的褐色斑点——像是落上去的灰尘，又像是天生就有的记号。\n\n它没有看你。它看着窗外的夜色。\n\n但你动了一下的时候，它立刻转过头来。\n\n警觉，但不害怕。\n\n它不会被困在屋子里。店员说，但它愿意为你留下来——至少今晚。",

    "猫": "你没有看见它。\n\n你先是感觉到脚踝有什么东西蹭了一下。\n\n低头——\n\n一只黑猫蹲在你脚边，尾巴尖轻轻拍着地面。它没有叫，只是抬眼看了你一眼。\n\n那一眼的意思是：我知道你是谁了。你还不知道我是谁。\n\n店员嗤笑了一声。它从来不主动蹭人。\n\n黑猫站起来，慢悠悠走到你椅子腿旁边，蜷成一团。\n\n它闭上眼睛。\n\n不是睡着了。是觉得这里安全。",

    "蟾蜍": "柜台下面传来一声很轻的咕。\n\n然后一只蟾蜍慢慢跳了出来。\n\n它跳得很慢，每跳一步都要停下来看看四周。皮肤是深褐色的，上面有细小的疙瘩——不漂亮，但有一种说不出的……老实。\n\n它跳到你鞋旁边，停住了。\n\n仰头。\n\n蟾蜍的脸很平，看不出表情。但你就是觉得它在等你说话。\n\n店员轻轻说：它不怕你。",

    "老鼠": "你先是听到窸窸窣窣的声音。\n\n然后一个灰色的小脑袋从柜台下面的缝隙里探出来，左右看了看。\n\n老鼠很小。小到你一开始以为是一团掉落的绒毛。\n\n它犹豫了很久——探出头，缩回去，再探出来。\n\n最后它跑了出来。\n\n不是朝你跑。是沿着墙根跑，跑到你椅子旁边，蹲下来开始洗脸。\n\n店员叹了口气。它怕人，但不怕你。你知道这意味着什么吗？",

    "侏儒蒲": "有什么东西从桌面上滚了过来。\n\n不，不是滚——是弹。\n\n侏儒蒲太小了，小到你以为是茶壶盖上的装饰掉了下来。\n\n它弹到你手边，停住了。\n\n浑身上下都是绒毛，圆滚滚的，两只小眼睛亮晶晶地看着你。\n\n它抖了抖——不是害怕，是在整理自己。\n\n它在努力让你觉得它好看。店员语气温柔了一点，它很少这么努力。",

    "护树罗锅": "如果不是店员看了一眼墙角，你根本不会发现它。\n\n护树罗锅看起来就是一截普普通通的树枝。\n\n但它动了一下。\n\n很慢。慢到你以为是风吹的。\n\n然后它从墙角走到了——不，是挪到了——桌腿旁边，停住。\n\n它没有看你。它看着地面。\n\n店员沉默了两秒：它想靠近你。",

    "猫狸子": "柜台后面的阴影里，亮起两盏琥珀色的灯。\n\n那是猫狸子的眼睛。\n\n它走出来的样子不像猫。像一位老人在散步。从容、缓慢，带着一种我不需要讨好任何人的自信。\n\n它走到你面前，停下来。\n\n仰头，看着你的眼睛。\n\n不是审视你。是在确认一件它早就知道的事。\n\n店员深吸一口气。它从不主动见客人。你是第三个。",

    "嗅嗅": "你听到叮的一声。\n\n然后一个黑乎乎的小东西从柜台后面窜了出来，速度极快，像一道黑色的闪电。\n\n它停在你脚边，仰头看你。\n\n嗅嗅。肚皮上的口袋鼓鼓囊囊的，不知道又从哪儿偷了一堆破烂。\n\n它歪头看了你两秒——\n\n突然伸出手，从口袋里掏出一枚亮晶晶的纽扣，放在你鞋面上。\n\n店员愣住了。……它从来没给过任何人东西。\n\n你要是不想要，也别当着它的面扔掉。",

    "双头水螈": "你先是看到水盆里泛起了涟漪。\n\n然后两个小脑袋从水面下探出来。\n\n左边那个头看着你，右边那个头看着左边那个头——好像在吵架，又好像在商量什么事。\n\n两个头同时转向你。\n\n一个头往前伸了伸，另一个头不情愿地跟着往前伸。\n\n店员轻声说：它们两个意见很少统一。但今天……倒是挺一致的。",

    "蒲绒绒": "有什么东西从货架上掉了下来。\n\n不是掉——是滚。\n\n蒲绒绒像一团毛线球一样滚到你脚边，弹了一下，停住了。\n\n它太软了。软到你觉得它不是动物，是一块会呼吸的棉花。\n\n它蹭了蹭你的鞋尖。\n\n然后打了个哈欠。\n\n店员忍不住笑了。它在你脚边打哈欠。你知道什么意思吗？它觉得你很安全。",

    "绝音鸟": "门后面有一片羽毛落下来。\n\n但你没有听到任何声音。\n\n绝音鸟站在柜台的边缘，灰蓝色的羽毛在暗光里几乎看不见。它看着你，嘴巴微微张开——\n\n但没有声音。\n\n它一生只叫一次。不是现在。\n\n店员安静了很久才说：它愿意让你看见它。这比叫声更难得。",

    "恶婆鸟": "你听到了一阵……不是声音，是振动。\n\n空气在轻轻抖，像有什么东西在远处敲鼓。\n\n然后恶婆鸟飞了出来。\n\n它的羽毛鲜艳得不像真的——橘红、翠绿、钴蓝，像打翻了一盒颜料。\n\n它在空中绕了一圈，落在你旁边的椅背上，歪头看你。\n\n店员皱了一下眉。它不吵的时候……还挺好看的。但它不吵的时候很少。\n\n它安静了。因为你在。",

    "弗洛伯毛虫": "你没有看见它。\n\n店员弯腰从柜台下面拿出一个罐子，放在桌上。\n\n罐子里有一条褐色的、胖胖的虫，一动不动地趴在莴苣叶子上。\n\n弗洛伯毛虫。\n\n它什么都没有做。只是在呼吸。\n\n店员看着你，又看看罐子。它不会主动走向任何人。它太慢了。\n\n但如果你愿意等它……它会一直活着。",

    "土扒貂": "你先是听到床底下有声音。\n\n不——这里没有床。是椅子下面。\n\n一团灰乎乎的东西从暗处窜出来，速度快到只剩下残影。\n\n然后它停住了。\n\n土扒貂。像一只灰貂，但更紧凑、更沉默。\n\n它看了你一眼，没有靠近，也没有后退。\n\n店员说：它在判断。不是判断你是不是好人——是判断你是不是会突然动。\n\n你不动的时候，它就会过来。",
}


def expand_scores(scores: dict) -> dict:
    """展开特殊标签为具体生物分数"""
    result = {}
    for key, value in scores.items():
        if key == "_all_owls":
            for c in OWL_CREATURES:
                result[c] = result.get(c, 0) + value
        elif key == "_non_owls":
            for c in CREATURES:
                if c not in OWL_CREATURES:
                    result[c] = result.get(c, 0) + value
        elif key == "_all_bugs":
            for c in BUG_CREATURES:
                result[c] = result.get(c, 0) + value
        elif key == "_all_reptiles":
            for c in REPTILE_CREATURES:
                result[c] = result.get(c, 0) + value
        elif key == "_all_birds":
            for c in BIRD_CREATURES:
                result[c] = result.get(c, 0) + value
        elif key == "_all_feather":
            for c in FEATHER_CREATURES:
                result[c] = result.get(c, 0) + value
        elif key == "_all_mammal":
            for c in MAMMAL_CREATURES:
                result[c] = result.get(c, 0) + value
        elif key == "_loyal":
            for c in LOYAL_CREATURES:
                result[c] = result.get(c, 0) + value
        elif key == "_smart":
            for c in SMART_CREATURES:
                result[c] = result.get(c, 0) + value
        elif key == "_all":
            for c in CREATURES:
                result[c] = result.get(c, 0) + value
        else:
            result[key] = result.get(key, 0) + value
    return result


class Answer(BaseModel):
    question_id: int
    option_label: Optional[str] = None
    free_text: Optional[str] = None


class QuizSubmit(BaseModel):
    answers: List[Answer]
    taboo_option: str
    email: EmailStr
    color: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
async def index():
    with open("/home/cris/.openclaw/workspace/pet-quiz/static/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/api/questions")
async def get_questions():
    return {"questions": QUESTIONS, "taboo": TABOO_QUESTION}


@app.post("/api/submit")
async def submit_quiz(data: QuizSubmit):
    scores = {c: 0 for c in CREATURES}
    color = data.color or ""

    # 计算常规题目分数
    for ans in data.answers:
        for q in QUESTIONS:
            if q["id"] == ans.question_id:
                if ans.option_label:
                    for opt in q.get("options", []):
                        if opt["label"] == ans.option_label:
                            expanded = expand_scores(opt.get("scores", {}))
                            for c, v in expanded.items():
                                if c in scores:
                                    scores[c] += v
                break

    # 应用忌讳问卷降权
    taboo_effects = {
        "A": {"弗洛伯毛虫": -10, "双头水螈": -10, "土扒貂": -10},
        "B": {"老鼠": -10, "猫": -2},
        "C": {"绝音鸟": -10, "护树罗锅": -10},
        "D": {},
    }
    if data.taboo_option in taboo_effects:
        for c, v in taboo_effects[data.taboo_option].items():
            if c in scores:
                scores[c] += v

    # 过滤负分生物
    valid_scores = {c: s for c, s in scores.items() if s > 0}
    if not valid_scores:
        valid_scores = scores

    # 排序，取前3-6个
    sorted_scores = sorted(valid_scores.items(), key=lambda x: x[1], reverse=True)

    # 确定展示数量：前3个必展示，如果第4个及以后分数差距不大（差距<3），也展示
    results = []
    if len(sorted_scores) > 0:
        results.append(sorted_scores[0])
        for i in range(1, len(sorted_scores)):
            if i < 3 or (sorted_scores[i][1] >= sorted_scores[0][1] - 3):
                results.append(sorted_scores[i])
            else:
                break

    # 构建返回数据
    top_creatures = [c for c, s in results]
    scenes = []
    for c in top_creatures:
        scene_text = SCENES.get(c, "")
        if color and c == "雪鸮":
            scene_text += f"\n\n你的颜色{color}好像让它想起了什么。"
        scenes.append({"creature": c, "score": scores[c], "scene": scene_text})

    # 店员总结
    if len(top_creatures) == 1:
        summary = f"今天倒是稀奇。\n\n这一位——他看着{top_creatures[0]}，不是谁都看得见的。\n\n他顿了一下。\n\n它今天……想认识你。"
    elif len(top_creatures) == 2:
        summary = f"今天倒是稀奇。\n\n这一位——他看着{top_creatures[0]}，不是谁都看得见的。\n这一位——看着{top_creatures[1]}，它蹭过的人，十个手指头数得过来。\n\n他顿了一下。\n\n它们今天……都想认识你。"
    else:
        mentions = []
        for i, c in enumerate(top_creatures[:3]):
            if i == 0:
                mentions.append(f"这一位——他看着{c}，不是谁都看得见的。")
            elif i == 1:
                mentions.append(f"这一位——看着{c}，它蹭过的人，十个手指头数得过来。")
            else:
                mentions.append(f"还有这一位——看着{c}，它三年没从墙缝里出来过了。")
        summary = "今天倒是稀奇。\n\n" + "\n".join(mentions) + "\n\n他顿了一下。\n\n它们今天……都想认识你。"

    return {
        "scores": dict(sorted_scores),
        "top_creatures": top_creatures,
        "scenes": scenes,
        "summary": summary,
        "email": data.email,
        "color": color,
    }


# 创建静态文件目录
os.makedirs("/home/cris/.openclaw/workspace/pet-quiz/static", exist_ok=True)
app.mount("/static", StaticFiles(directory="/home/cris/.openclaw/workspace/pet-quiz/static"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
