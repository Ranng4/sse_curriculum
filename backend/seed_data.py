# AI-generated: seed data script for stock investment forum
"""种子数据脚本 — 通过后端 API 批量创建投资论坛内容。"""

from __future__ import annotations

import json
import random
import time
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8000/api/v1"


def api(method: str, path: str, body: dict | None = None, token: str | None = None) -> dict:
    url = f"{BASE}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        msg = e.read().decode()
        print(f"  [ERROR] {method} {path} -> {e.code}: {msg[:120]}")
        raise
    if result.get("code") != 0:
        raise RuntimeError(f"API error: {result.get('message')}")
    return result.get("data")


def register_user(phone: str, nickname: str, password: str = "Pass123456") -> tuple[str, str]:
    data = api("POST", "/auth/register", {
        "method": "phone", "phone": phone, "password": password,
        "nickname": nickname, "verification_code": "1234",
    })
    return data["user_id"], data["token"]["access_token"]


def login(account: str, password: str = "Pass123456") -> str:
    return api("POST", "/auth/login", {"account": account, "password": password})["access_token"]


USERS = [
    {"nickname": "价值投资者老张", "phone": "13800000101"},
    {"nickname": "量化小王子",       "phone": "13800000102"},
    {"nickname": "茅台守望者",       "phone": "13800000103"},
    {"nickname": "趋势交易员Lisa",   "phone": "13800000104"},
    {"nickname": "小散户的日常",     "phone": "13800000105"},
    {"nickname": "宏观观察者",       "phone": "13800000106"},
    {"nickname": "技术分析派阿强",   "phone": "13800000107"},
    {"nickname": "基金定投日记",     "phone": "13800000108"},
    {"nickname": "港股研究员",       "phone": "13800000109"},
    {"nickname": "美股夜猫子",       "phone": "13800000110"},
    {"nickname": "期货狙击手",       "phone": "13800000111"},
    {"nickname": "财经小辣椒",       "phone": "13800000112"},
    {"nickname": "稳健理财阿明",       "phone": "13800000113"},
    {"nickname": "新股猎人",         "phone": "13800000114"},
    {"nickname": "数据分析师Jack",   "phone": "13800000115"},
]

# ── 帖子模板 ──

POSTS = {
    "a-share": [
        {
            "title": "贵州茅台600519：长期护城河是否依然坚固？",
            "content": (
                "茅台近期股价回调引发了市场广泛讨论。从基本面来看，茅台的品牌护城河、"
                "现金流质量和分红能力依然是A股顶级。\n\n"
                "但当前消费环境的变化不可忽视：\n"
                "1. 高端白酒消费场景减少\n2. 渠道库存压力增大\n"
                "3. 年轻一代对白酒消费意愿下降\n\n"
                "个人认为，茅台短期有压力，但长期看，稀缺性和品牌价值决定了它仍然是优质资产。"
            ),
            "post_type": "longform", "stock_codes": ["600519"],
        },
        {
            "title": "今天大盘走势分析：量能萎缩，方向选择在即",
            "content": (
                "上证指数在3300点附近反复震荡，成交量较前几日明显萎缩。\n"
                "技术面看：5日均线走平，MACD红柱缩短，KDJ高位钝化。\n"
                "短期可能面临方向选择，建议控制仓位。"
            ),
            "post_type": "realtime", "stock_codes": [],
        },
        {
            "title": "宁德时代300750：新能源电池龙头的天花板在哪？",
            "content": (
                "宁德时代作为全球动力电池龙头，市占率保持领先。但市场担忧有二：\n"
                "1. 行业竞争加剧，比亚迪等对手崛起\n2. 海外扩张面临地缘政治风险\n\n"
                "技术层面，麒麟电池和钠离子电池的研发进展值得关注。"
            ),
            "post_type": "longform", "stock_codes": ["300750"],
        },
        {
            "title": "银行股估值修复行情能持续吗？",
            "content": (
                "最近银行板块涨势不错，四大行和招行都有不错表现。驱动因素：\n"
                "1. 高股息策略受追捧 2. 地产风险逐步出清 3. 利差修复预期\n"
                "个人比较看好招行和宁波银行，零售银行转型路径清晰。"
            ),
            "post_type": "normal", "stock_codes": ["600036", "002142"],
        },
        {
            "title": "医药板块触底反弹，CXO值得关注",
            "content": (
                "经历了两年多的调整，医药板块估值已经回到历史低位。\n"
                "重点关注：CXO（药明康德、康龙化成）—海外订单回暖；创新药—政策边际改善；中药—政策支持明确。"
            ),
            "post_type": "normal", "stock_codes": ["603259", "300759"],
        },
        {
            "title": "[实时] 半导体盘中异动，中芯国际涨超5%",
            "content": "中芯国际688981盘中突然放量拉升，涨超5%，带动整个半导体板块走强。消息面上，有传闻称先进制程取得突破。",
            "post_type": "realtime", "stock_codes": ["688981"],
        },
    ],
    "hk-stock": [
        {
            "title": "腾讯控股0700：回购力度加大，估值是否已充分反映风险？",
            "content": (
                "腾讯今年以来持续加大回购力度，每天约10亿港元的回购规模。\n"
                "PE已回落到15倍左右，处于历史低位。主要风险：国内游戏监管、广告收入放缓。\n"
                "但微信生态的护城河价值被低估，视频号商业化前景值得期待。"
            ),
            "post_type": "longform", "stock_codes": ["0700"],
        },
        {
            "title": "港交所0388：互联互通持续扩容的受益者",
            "content": "港交所长期受益于沪深港通交易量增长、中概股回归、人民币柜台拓展。当前估值合理，股息率约2.5%。",
            "post_type": "normal", "stock_codes": ["0388"],
        },
    ],
    "us-stock": [
        {
            "title": "英伟达NVDA：算力需求是否被高估了？",
            "content": (
                "英伟达股价今年涨幅惊人。乐观：大模型训练需求仍在爆发，CUDA生态护城河极深。\n"
                "谨慎：客户集中度过高，竞争对手追赶，估值已反映极度乐观预期。"
            ),
            "post_type": "longform", "stock_codes": ["NVDA"],
        },
        {
            "title": "特斯拉TSLA：Robotaxi能否成为下一增长引擎？",
            "content": "特斯拉聚焦Robotaxi和FSD，关键问题：FSD能否实现真正的无人驾驶？Robotaxi商业化时间表？传统汽车增速放缓如何应对？",
            "post_type": "normal", "stock_codes": ["TSLA"],
        },
    ],
    "future": [
        {
            "title": "黄金期货创历史新高，还能追吗？",
            "content": (
                "COMEX黄金突破前高。驱动：美联储降息预期、全球央行增持、地缘风险溢价。\n"
                "技术面已突破整理区间，短期有超买风险但趋势完好，回调到支撑位可分批建仓。"
            ),
            "post_type": "normal", "stock_codes": [],
        },
        {
            "title": "螺纹钢期货空头逻辑：地产需求疲软",
            "content": "螺纹钢近期走势偏弱，核心逻辑是地产新开工面积持续下滑。供给端钢厂减产意愿不强，供需格局偏空。",
            "post_type": "normal", "stock_codes": [],
        },
    ],
    "value-investing": [
        {
            "title": "真正的价值投资：如何评估企业的内在价值？",
            "content": (
                "价值投资的核心不是低PE，而是用低于内在价值的价格买入优秀企业。\n"
                "框架：DCF折现、ROE持续性、护城河宽度、管理层能力与诚信。\n"
                "简单方法：如果这家公司明天退市，你愿意以当前市值全资收购吗？"
            ),
            "post_type": "longform", "stock_codes": [],
        },
        {
            "title": "巴菲特减持比亚迪的启示：何时应该卖出？",
            "content": (
                "巴菲特从2008年买入比亚迪到2022年开始减持，卖出比买入更难。\n"
                "卖出条件：基本面发生变化、估值远超合理范围、发现更好机会、投资框架不再适用。"
            ),
            "post_type": "normal", "stock_codes": ["002594"],
        },
    ],
    "quant-investing": [
        {
            "title": "多因子选股模型实战心得：动量因子在A股的表现",
            "content": (
                "回测发现：中期动量(3-6月)在A股有显著正收益；短期反转在市值较小的股票上更有效；\n"
                "行业中性化处理后因子稳定性明显提升。注意：A股政策市特征明显，需叠加主观判断。"
            ),
            "post_type": "longform", "stock_codes": [],
        },
        {
            "title": "[数据] A股各行业估值分位数（本周更新）",
            "content": (
                "银行35%分位(低估)、食品饮料45%(合理偏低)、医药生物20%(低估)、\n"
                "电子65%(合理偏高)、新能源25%(低估)、煤炭70%(偏高)。数据来源：Wind。"
            ),
            "post_type": "normal", "stock_codes": [],
        },
    ],
    "fund-investing": [
        {
            "title": "ETF定投实盘记录：每月5000元，目标年化10%",
            "content": (
                "组合：沪深300ETF(510300)40% + 创业板ETF(159915)30% + 中证红利(515080)20% + 恒生科技(513180)10%。\n"
                "策略：每月15日定投，每季度再平衡。目前持仓3个月累计收益2.3%。"
            ),
            "post_type": "longform", "stock_codes": ["510300", "159915", "515080", "513180"],
        },
        {
            "title": "指数基金 vs 主动基金：全面对比分析",
            "content": (
                "指数基金：费率低(0.15%-0.5%)、透明度高、不受经理变动影响。\n"
                "主动基金：有机会获取超额收益、灵活应对市场变化，但费率较高(1.5%)、业绩持续性存疑。\n"
                "建议：核心仓位指数基金，卫星仓位少量配置优秀主动基金。"
            ),
            "post_type": "normal", "stock_codes": [],
        },
    ],
    "ipo-bond": [
        {
            "title": "下周新股申购日历（更新）",
            "content": (
                "周一科创板1只(半导体设备)、周二创业板1只(医疗器械)、周三主板2只(消费电子、化工)、周五科创板1只(新材料)。\n"
                "重点关注周一的半导体设备公司，行业景气度向上。"
            ),
            "post_type": "normal", "stock_codes": [],
        },
        {
            "title": "可转债打新一年总结：中签率下降但收益稳定",
            "content": (
                "今年申购42次，中签7次(17%)，首日平均涨幅21%，累计收益约2800元。\n"
                "由于参与人数增加中签率下降，但每次中签的收益还是比较稳定的。"
            ),
            "post_type": "normal", "stock_codes": [],
        },
    ],
    "macro-strategy": [
        {
            "title": "美联储降息周期开启，A股和港股怎么看？",
            "content": (
                "降息对A股：人民币汇率压力减轻→外资回流预期；国内货币政策空间打开；成长股估值修复。\n"
                "对港股：流动性改善直接受益、科技股估值重估、高股息资产吸引力下降。总体看好降息周期下的中国资产。"
            ),
            "post_type": "longform", "stock_codes": [],
        },
        {
            "title": "2024下半年宏观展望：经济温和复苏",
            "content": (
                "GDP增速5%左右，CPI低位温和回升，货币政策仍有空间，专项债加速发行。\n"
                "核心风险：房地产企稳节奏、外部需求走弱、地缘政治。策略：中等仓位逢低布局顺周期。"
            ),
            "post_type": "normal", "stock_codes": [],
        },
    ],
    "company-research": [
        {
            "title": "[深度] 美的集团000333：从家电龙头到科技集团",
            "content": (
                "业务结构：暖通空调42%、消费电器33%、机器人与自动化(库卡)25%←亮点。\n"
                "核心竞争力：数字化转型领先(工业互联网连接10万+工厂)、全球化(海外营收40%+)、研发费用率4%+。\n"
                "PE约14倍，处于历史中位以下，具有较好安全边际。"
            ),
            "post_type": "longform", "stock_codes": ["000333"],
        },
    ],
    "industry-research": [
        {
            "title": "光伏行业深度：产能出清还需要多久？",
            "content": (
                "光伏产业链价格全面下跌：硅料从300跌到60元/kg、硅片毛利率转负、组件跌破1元/W。\n"
                "出清预计还需6-12个月。关注指标：龙头亏损幅度、二三线停产比例、银行抽贷。\n"
                "穿越周期后行业集中度将大幅提升，通威、隆基将受益。目前是左侧布局时点需分批建仓。"
            ),
            "post_type": "longform", "stock_codes": ["601012", "600438"],
        },
    ],
    "stock-research": [
        {
            "title": "比亚迪002594深度研究：DM5.0为何改变游戏规则？",
            "content": (
                "DM5.0百公里亏电油耗2.9L！发动机热效率46.06%全球最高，综合续航突破2000km。\n"
                "传统合资品牌在混动技术上已被拉开代际差距，比亚迪市占率有望进一步提升。\n"
                "2024年净利润预计350-400亿，PE约20倍，合理估值区间内。"
            ),
            "post_type": "longform", "stock_codes": ["002594"],
        },
    ],
    "qa-help": [
        {
            "title": "新手求教：定投ETF应该选哪几只？",
            "content": (
                "刚工作两年想开始做定投，每月3000元预算。看了很多攻略越看越迷糊：\n"
                "1.定投几只ETF合适？2.宽基和行业ETF怎么搭配？3.定投日选月初还是月末？4.需要设置止损吗？感谢各位大佬！"
            ),
            "post_type": "normal", "stock_codes": [],
        },
    ],
    "newbie-questions": [
        {
            "title": "请问「除权除息」是什么意思？对股价有什么影响？",
            "content": (
                "看到有的股票突然跌了一大截，同事说是除权除息，不太理解。\n"
                "为什么分红会导致股价下跌？是不是等于什么都没得到？分红的意义是什么？希望有大佬通俗解释！"
            ),
            "post_type": "normal", "stock_codes": [],
        },
    ],
    "investment-help": [
        {
            "title": "被套30%了怎么办？在线等，挺急的",
            "content": (
                "去年追高买了某新能源股票，成本52元现在只剩36元，亏损接近30%。\n"
                "期间几次反弹都没出，现在越套越深。三个选择：1.死扛等回本 2.止损卖出 3.低位补仓摊薄成本。求前辈指条明路！"
            ),
            "post_type": "normal", "stock_codes": [],
        },
    ],
}

COMMENTS = [
    "感谢分享，写得很有深度！我也在关注这个板块。",
    "楼主的分析很到位，补充一点：政策面也有利好预期。",
    "技术面来看短期确实需要谨慎，但中长期逻辑没变。",
    "同意。我一直在定投，成本已经拉下来了。",
    "估值合理不代表马上会涨，需要催化剂。耐心等待。",
    "看了楼主的分析，我今天加了一点仓位。",
    "说得好！投资就是认知变现，深入研究才能赚到认知范围内的钱。",
    "我持不同观点——当前市场风险偏好太低，利好都被忽视了。",
    "建议分批建仓，不要一次性满仓，给自己留余地。",
    "请问楼主对明年的业绩预期怎么看？",
    "这个票我跟了两年了，管理层确实靠谱，长期持有没问题。",
    "感谢推荐！加入自选跟踪一下。",
    "新手想问一下，现在入场是不是太晚了？",
    "大方向赞同，但节奏上可以再等等，等右侧确认。",
    "数据很详实，收藏了！每个月来回顾一下。",
    "和我的持仓很像，英雄所见略同。",
    "提醒大家注意风险，投资有风险入市需谨慎。",
    "关注这个赛道很久了，终于看到有人深度分析了。",
    "楼主的思路很清晰，学到了。希望多分享这类干货。",
    "总结得很全面！补充一个角度：从全球资产比较来看…",
    "估值修复行情一般持续3-6个月，现在才刚开始。",
    "每次回调都是上车机会，前提是你对这个票有足够认知。",
    "赞一个！干货满满，比那些只会喊单的人靠谱多了。",
    "请教楼主一个问题：如果大盘继续下跌，这个票能抗住吗？",
    "其实还有一个隐性利好市场还没反映，值得深挖。",
]


def _fetch_board_map() -> dict[str, str]:
    sections = api("GET", "/forum/sections")
    mapping = {}
    for section in sections:
        for board in section.get("boards", []):
            mapping[board["slug"]] = board["id"]
            mapping[board["slug"] + "_name"] = board["name"]
    return mapping


def main():
    print("=" * 60)
    print("  融智论坛 - 种子数据生成器")
    print("=" * 60)

    # Step 1: 注册/登录用户
    print("\n[1/6] 创建用户...")
    sessions = []
    for u in USERS:
        try:
            uid, token = register_user(u["phone"], u["nickname"])
            print(f"  + {u['nickname']}")
        except Exception:
            time.sleep(0.2)
            token = login(u["phone"])
            print(f"  = {u['nickname']} (existing)")
        sessions.append({"token": token, "nickname": u["nickname"]})
        time.sleep(0.1)
    print(f"  共 {len(sessions)} 个用户就绪")

    # Step 2: 建立关注关系
    print("\n[2/6] 建立关注关系...")
    # 重新获取user_id（通过profile API）
    user_ids = []
    for s in sessions:
        try:
            profile = api("GET", "/profile/me", token=s["token"])
            user_ids.append(profile["user_id"])
        except Exception:
            user_ids.append(None)

    follow_count = 0
    for i, s in enumerate(sessions):
        if user_ids[i] is None:
            continue
        targets = random.sample(
            [(j, user_ids[j]) for j in range(len(user_ids)) if j != i and user_ids[j]],
            k=min(random.randint(2, 4), len(user_ids) - 1),
        )
        for j, target_id in targets:
            try:
                api("POST", f"/social/follows/{target_id}", token=s["token"])
                follow_count += 1
            except Exception:
                pass
            time.sleep(0.03)
    print(f"  {follow_count} 条关注关系已建立")

    # Step 3: 发帖
    print("\n[3/6] 发布帖子...")
    board_map = _fetch_board_map()
    all_posts = []
    user_idx = 0
    for board_slug, post_list in POSTS.items():
        bid = board_map.get(board_slug)
        if not bid:
            print(f"  [WARN] 未找到板块: {board_slug}")
            continue
        for template in post_list:
            s = sessions[user_idx % len(sessions)]
            try:
                post = api("POST", "/content/posts", {
                    "board_id": bid,
                    "title": template["title"],
                    "content": template["content"],
                    "post_type": template["post_type"],
                    "stock_codes": template["stock_codes"],
                }, token=s["token"])
                board_name = board_map.get(board_slug + "_name", board_slug)
                print(f"  + [{board_name}] {template['title'][:40]}...")
                all_posts.append(post)
                user_idx += 1
                time.sleep(0.08)
            except Exception as e:
                print(f"  [ERR] {e}")
                time.sleep(0.2)
    print(f"  共发布 {len(all_posts)} 篇帖子")

    # Step 4: 评论
    print("\n[4/6] 添加评论...")
    comment_count = 0
    for post in all_posts:
        num = random.randint(2, 6)
        for _ in range(num):
            s = random.choice(sessions)
            try:
                api("POST", f"/content/posts/{post['id']}/comments", {
                    "content": random.choice(COMMENTS),
                }, token=s["token"])
                comment_count += 1
                time.sleep(0.04)
            except Exception:
                pass
    print(f"  {comment_count} 条评论已添加")

    # Step 5: 点赞和收藏
    print("\n[5/6] 点赞 & 收藏...")
    like_count = fav_count = 0
    for post in all_posts:
        likers = random.sample(sessions, k=min(random.randint(3, 8), len(sessions)))
        for s in likers:
            try:
                api("POST", f"/content/posts/{post['id']}/like", token=s["token"])
                like_count += 1
                time.sleep(0.03)
            except Exception:
                pass
        favers = random.sample(sessions, k=min(random.randint(1, 5), len(sessions)))
        for s in favers:
            try:
                api("POST", f"/content/posts/{post['id']}/favorite", token=s["token"])
                fav_count += 1
                time.sleep(0.03)
            except Exception:
                pass
    print(f"  点赞: {like_count} | 收藏: {fav_count}")

    # Step 6: 投资偏好
    print("\n[6/6] 更新投资偏好...")
    prefs = [
        {"focus_markets": ["a_share", "fund"], "risk_preference": "C2"},
        {"focus_markets": ["a_share", "hk_stock", "us_stock"], "risk_preference": "C4"},
        {"focus_markets": ["a_share"], "risk_preference": "C3"},
        {"focus_markets": ["a_share", "future"], "risk_preference": "C5"},
        {"focus_markets": ["fund", "bond"], "risk_preference": "C1"},
        {"focus_markets": ["a_share", "hk_stock"], "risk_preference": "C3"},
        {"focus_markets": ["us_stock"], "risk_preference": "C4"},
    ]
    for i, s in enumerate(sessions[: len(prefs)]):
        try:
            api("PATCH", "/profile/investment-preferences", prefs[i], token=s["token"])
            time.sleep(0.05)
        except Exception:
            pass
    print("  投资偏好已更新")

    print("\n" + "=" * 60)
    print(f"  种子数据生成完成！")
    print(f"  用户: {len(sessions)} | 帖子: {len(all_posts)}")
    print(f"  评论: {comment_count} | 点赞: {like_count} | 收藏: {fav_count}")
    print("=" * 60)
    print("\n  http://localhost:5173 查看效果")


if __name__ == "__main__":
    main()
