from .json_schema import json_schema

PREFACE_PROMPT = """
    <role>
    你是一个专业的科技内容编辑，擅长撰写文章导读和前言，了解中国互联网语境内微信公众号文章的特点、文风。
    </role>
    <instruction>
    1. 基于提供的元数据信息（标题、来源、作者、描述等）撰写一段引人入胜的导读
    2. 导读应该简明扼要地介绍文章的背景和重要性
    3. 突出作者的专业背景和文章的可信度
    4. 用优雅的语言勾勒文章的主要内容
    5. 长度控制在50-80字之间
    6. 你的读者已经高度了解AI和科技的发展（但不需要直接提及他们），年龄层是20-40，所以语言要成熟，避免浅显的比喻和语句。
    </instruction>
    <metadata>
    {metadata}
    </metadata>
"""

CONTENT_REVIEW_PROMPT="""
        <role>公众号写手</role>  
        <instruction>通读整篇文章，检查是否存在内容重复或过度使用的短语。删除或精简重复表达同一观点的段落或部。检查并删除频繁出现的短语或句式（例如“试想一下……”“想象一下...”）。删除或减少第二人称的问句。
        直接在我提供的文章上修改，而不是仅仅提供建议。不要包含```，直接输出你修改后的完整文章。
        </instruction>
        <article>
        {article}
        </article>
    """

def SUMMARIZE_PROMPT(original_article):
    base_prompt = """
        <role>
        You are a professional content editor who excels at identifying and extracting the most important information from articles while maintaining their core message and key points.
        </role>
        <instruction>
        1. Analyze the provided article and identify its main points, key arguments, and essential details.
        2. Remove redundant information, excessive examples, and less relevant tangents.
        3. Maintain the article's core message and key insights.
        4. Keep the most impactful examples and statistics.
        5. Ensure the output is coherent and flows naturally.
        6. Aim to reduce the length while preserving the article's value.
        </instruction>
        <original-article>
        {original_article}
        </original-article>
    """
    return base_prompt.format(original_article=original_article)

def OUTLINE_PROMPT(original_article):
    base_prompt = """
        <role>
        你是一个科技公众号写手，擅长在写文章之前以 json 的格式撰写文章大纲
        </role>
        <output-format>
        json
        </output-format>
        <original-article>
        {original_article}
        </original-article>
        <instruction>
            1. 根据用户提供的 original-article 生成一篇新的文章大纲，需要符合微信公众号的风格和习惯
            2. 仅输出大纲，不要完成文章的撰写
            3. 大纲要包含有趣的细节，越引人瞩目的细节、事实，应该越早出现。大纲不是一些 phrase，而是 complete sentences
            4. 文章不应该严谨，而是让人想读下去。不要冗长。
            5. 输出纯 json 并且给每个节点都设置 node_id，可以嵌套最多 1 层。
            6. 永远输出中文，但人名、专有名词可以用英文
            7. 永远输出 json
            8. 大标题和小标题，要犀利、适合中文公众号读者、抓眼球
        </instruction>
        <json-schema>
        {schema}
        </json-schema>
    """
    return base_prompt.format(
        original_article=original_article,
        schema=str(json_schema())
    )

PARAGRAPH_PROMPT = """
    ## 角色
    你是一个微信公众号写手，我了解中国互联网语境内微信公众号文章的特点、文风。

    ## 公众号写作技巧
    请你学习一下 AI 写作和公众号写手的风格区别。

    3. Quote Integration
    AI: "他说道...", "据他所说..."
    公众号: "RDS的一位副总裁跟我说", "他就说，'是的，但我还是要走了'"

    4. Descriptive Language
    AI: "工作很困难", "变化很大"
    公众号: "老鼠赛跑", "雷厉风行、近乎军事化"

    5. Structure
    AI: "第一部分", "第二部分"
    公众号: "55岁，重回工程师岗位"

    6. Professional Tone
    AI: "需要注意", "值得关注"
    公众号: "成功渡过难关", "文化方面的转变是必要的"

    7. Sentence Patterns
    AI: 简单并列句
    公众号: 递进式表达，如"不管什么事，你必须先变成个混蛋才能做成"

    8. Technical Writing
    AI: 直接解释概念
    公众号: 通过类比解释，如用3D打印机类比代码生成

    9. Interview Style
    AI: "问：...答：..."
    公众号: 自然对话转换，保留个性化表达

    10. Language Choice
    AI: "这个问题很重要"
    公众号: "这是个巨大的希望"

    11. Narrative Elements
    AI: 按时间顺序陈述事实
    公众号: 穿插个人故事、观点碰撞

    ## 指令
    1. 阅读用户提供的背景信息作为事实依据 {original_article}
    2. 将要点展开写出 EXACTLY 1-3 个科技公众号的段落（要点如下：{node}）
    3. 采用你刚刚学习过的公众号写作技巧，确保写作风格是接地气、生动、有趣，不像普通 AI 一样机械、拗口
    4. 确保段落结构清晰，逻辑连贯，避免使用任何XML标签。
    5. 不要捏造事实，一切以提供给你的信息为准
    6. 如果这是一个采访，则强调主持人和嘉宾之间的观点碰撞。
    7. 你的读者已经高度了解AI和科技的发展，年龄层是20-40，所以语言要成熟，避免浅显的比喻和语句。
    8. 不要使用第一人称和第二人称的句子（我、你、我们、你们、我们认为、我认为、你怎么看，你认为呢，你觉得呢...）。删除感叹。删除比喻。
"""

WHOLE_ARTICLE_PROMPT = """
    <instruction>
    阅读 json 并合并每个节点的 title 和 full_text（如果有），输出一个 Markdown 格式的文章。Between the article's main title and before the body，include a 亮点 section in bullet points.
    </instruction>
    <insights>
    {insights}
    </insights>
    <json>
    {outline}
    </json>
    """

def generate_final_article(title, insights, outline, transcript, metadata, preface):
    body = ""
    link = ""
    for node in outline:
        body += f"""## {node['title']}\n{node['full_text']}\n"""
    if transcript.strip():
        transcript = f"## 详细对话\n{transcript}"
    if metadata:
        link = metadata["link"]
        link = f"_原链接：{link}_"
    return f"""# {title}\n\n>{preface}\n\n## 亮点\n{insights}\n\n{body}\n\n{transcript}\n\n{link}"""
    
INSIGHTS_PROMPT = """
    <original-article>
    {original_article}
    </original-article>
    <instructions>
    请仔细阅读原文，找出 3-5 个最引人注目且与常识偏离最大的重要事实、陈述、见解或统计数据。
    重点挑选那些可能因其出人意料、大胆主张或颠覆性影响而引发强烈反应或广泛讨论的细节。
    避免任何解释或解读（如“这表明/说明/意味着……”）；仅需提取和突出这些具有冲击力的信息点。
    回答应直接引用文章中的独特事实，不需解释，仅提供准确的内容。
    每条内容用单行简洁表达，无需加标题或标注来源，如“某人认为/表示……”等，仅陈述核心信息。
    必须用中文的 bullet points 回复，除了人名和特殊名词、品牌之外。
    </instructions>
    """

TRANSCRIPT_PROMPT = """
    <original-article>
    {original_article}
    </original-article>
    <outline>
    {outline}
    </outline>
    <instructions>
    You are writing the transcript section of an article. Only if the original-article contains a timestamped speech transcript of an interview involving multiple people, you need to do the following:
    1. remove parts of the speech unrelated to outline.
    2. translate the transcript into chinese, but keep special nouns and tech terms in English.
    3. Output in this line by line format (Replace "speaker name" with real name):
        Speaker Name: content
        Speaker Name: content
        Speaker Name: content
    otherwise, absolutely return an empty string with zero explanation
    </instructions>
    """

FACT_CHECKER_PROMPT = """
    <source-material>
    {original_article}
    </source-material>
    <article>
    {final_article}
    </article>
    <instructions>
    Your job is to check if a final article is 100% factually supported by source material.
    Check for names, date, ideas, special nouns, opinions. Check which person expressed which ideas. Give a factual score out of 100.
    </instructions>
    """