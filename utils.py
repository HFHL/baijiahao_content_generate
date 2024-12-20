# utils.py

import os
import zipfile
import shutil
import openai
import json
import base64
import logging
import datetime
from config import API_KEY, BASE_URL, MODEL_NAME, PROMPT_FILE, UPLOAD_FOLDER, SAVED_FOLDER
from PIL import Image
import io

# 设置OpenAI相关参数
openai.api_key = API_KEY
openai.api_base = BASE_URL

def allowed_file(filename):
    """
    检查文件是否为允许的类型（仅限zip文件）。
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'zip'}

def extract_all_zips(dir_path):
    """
    递归解压指定目录下的所有zip文件，并在解压后删除原zip文件。
    """
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.lower().endswith('.zip'):
                full_path = os.path.join(root, file)
                extract_path = os.path.splitext(full_path)[0]
                with zipfile.ZipFile(full_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
                os.remove(full_path)
                # 解压后可能还有子zip，递归处理
                extract_all_zips(extract_path)

def build_directory_tree(path):
    """
    构建指定路径的目录树结构，包含子目录和图片文件。
    """
    tree = {"name": os.path.basename(path), "path": path}
    dirs = []
    images = []
    for entry in os.scandir(path):
        if entry.is_dir():
            dirs.append(build_directory_tree(entry.path))
        elif entry.is_file():
            # 假设图片文件后缀
            if entry.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                images.append(entry.name)
    # 如果有子目录，则children存放子目录树
    if dirs:
        tree["children"] = dirs
    # 如果有图片
    if images:
        tree["images"] = images
    return tree

def build_jstree_format(tree, parent_id="#"):
    """
    将自定义的目录树结构转换为jsTree需要的格式。
    """
    jstree = []
    node_id = os.path.join(parent_id, tree["name"]) if parent_id != "#" else tree["name"]
    node_id = node_id.replace("\\", "/")  # 替换Windows路径分隔符为/
    node = {
        "id": node_id,
        "text": tree["name"],
        "children": []
    }
    if "children" in tree:
        for child in tree["children"]:
            child_jstree = build_jstree_format(child, node_id)
            node["children"].extend(child_jstree)
    if "images" in tree:
        for image in tree["images"]:
            image_id = os.path.join(node_id, image).replace("\\", "/")
            node["children"].append({
                "id": image_id,
                "text": image,
                "icon": "jstree-file",
                "children": False
            })
    jstree.append(node)
    logging.debug(f"节点添加: {node}")
    return jstree

def load_prompts():
    """
    从PROMPT_FILE加载提示模板。
    """
    if not os.path.exists(PROMPT_FILE):
        raise FileNotFoundError(f"Prompt file not found: {PROMPT_FILE}")
    with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def compress_image(image_path, max_size=(800, 800), quality=70):
    """
    压缩并调整图片大小。
    
    :param image_path: 图片文件的路径
    :param max_size: 图片的最大尺寸（宽, 高）
    :param quality: 压缩质量（1-100）
    :return: 压缩后的图片二进制数据
    """
    image = Image.open(image_path)
    image.thumbnail(max_size, Image.LANCZOS)  # 使用LANCZOS替代ANTIALIAS
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=quality)  # 压缩图片
    return buffer.getvalue()

def encode_image_to_base64(image_path):
    """
    将压缩后的图片转换为Base64编码。
    
    :param image_path: 图片文件的路径
    :return: Base64编码的字符串
    """
    compressed_image = compress_image(image_path)
    return base64.b64encode(compressed_image).decode('utf-8')

def sanitize_path(path):
    """
    对路径进行清理，确保其安全性。
    
    :param path: 输入的路径字符串
    :return: 清理后的路径字符串
    """
    return os.path.normpath(path)

def get_image_paths(path):
    """
    获取指定路径下所有图片文件的完整路径。
    
    :param path: 目录路径
    :return: 图片文件路径的列表
    """
    image_extensions = ('.png', '.jpg', '.jpeg', '.gif')
    image_paths = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.lower().endswith(image_extensions):
                image_paths.append(os.path.join(root, file))
    return image_paths

def calculate_cost(prompt_tokens, completion_tokens):
    """
    计算API调用成本。
    
    :param prompt_tokens: 提示使用的tokens数量
    :param completion_tokens: 补全使用的tokens数量
    :return: (cost_usd, cost_cny)
    """
    # 费用计算参数
    GROUP_MULTIPLIER = 1  # 分组倍率
    MODEL_MULTIPLIER = 1.25  # 模型倍率 gpt-4o
    COMPLETION_MULTIPLIER = 1  # 补全倍率
    BASE_UNIT = 500000  # 基础单位
    USD_TO_CNY = 7.13  # 美元兑人民币汇率
    
    cost_usd = (GROUP_MULTIPLIER * MODEL_MULTIPLIER * 
               (prompt_tokens + completion_tokens * COMPLETION_MULTIPLIER) / BASE_UNIT)
    cost_cny = cost_usd * USD_TO_CNY
    return cost_usd, cost_cny

def build_prompt(template_key, image_path, use_url=False):
    """
    根据指定的模板类型和图片路径构建GPT API的提示信息。
    
    :param template_key: 模板类型的键
    :param image_path: 图片文件的路径
    :param use_url: 是否使用外部存储的图片URL
    :return: 构建好的提示字符串
    """
    prompts = load_prompts()
    p = prompts.get(template_key, {})
    instructions = p.get("instructions", "")
    necessary = p.get("necessary", [])
    auxiliary = p.get("auxiliary", [])

    if use_url:
        # 上传图片并获取URL（此方案用户不需要）
        image_url = upload_image_to_storage(image_path)
        if not image_url:
            return "无法上传图片到存储服务。"
        # 准备消息内容
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "请详细描述这张图片的内容。"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    }
                ]
            }
        ]
    else:
        # 压缩并编码图片为Base64
        base64_image = encode_image_to_base64(image_path)
        print(f"图片大小: {os.path.getsize(image_path) / 1024:.2f} KB")
        # 准备消息内容
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "请详细描述这张图片的内容。"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]

    # 序列化消息内容为JSON字符串
    message_content = json.dumps(messages)

    # 构建最终的提示
    prompt = instructions + "\n" + \
             "必要要求条件：" + "\n".join(necessary) + "\n" + \
             "辅助要求条件：" + "\n".join(auxiliary) + "\n\n" + \
             f"{message_content}\n" + \
             f"请根据上述图像内容生成文案。\n"
    return prompt.strip()

def call_gpt_api(prompt):
    """
    调用OpenAI的ChatCompletion API获取生成的文案。
    
    :param prompt: 提示信息
    :return: (生成的文案, usage信息)
    """
    try:
        response = openai.ChatCompletion.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "你是一个优秀的创意文案作者。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800,
        )
        return response.choices[0].message.content, response.usage
    except openai.error.OpenAIError as e:
        # 记录错误日志
        logging.error(f"OpenAI API调用失败: {e}")
        return "生成文案失败，请稍后再试。", None

def save_generated_text(image_path, generated_text):
    """
    将生成的文案保存到文本文件中。
    
    :param image_path: 图片文件的路径
    :param generated_text: 生成的文案
    """
    # 定义保存文案的目录
    texts_dir = os.path.join(os.path.dirname(image_path), 'generated_texts')
    os.makedirs(texts_dir, exist_ok=True)
    # 定义文案文件名
    text_filename = os.path.splitext(os.path.basename(image_path))[0] + '.txt'
    text_path = os.path.join(texts_dir, text_filename)
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write(generated_text)

def save_all_items(saved_folder, items):
    """
    将所有生成的图片和文案保存到指定的保存目录中。

    :param saved_folder: 保存目录的根路径
    :param items: 包含图片路径和生成文案的列表
    :return: 保存后的目录路径
    """
    # 创建一个以当前时间为名称的子目录，避免文件冲突
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    target_dir = os.path.join(saved_folder, f"save_{timestamp}")
    images_dir = os.path.join(target_dir, 'images')
    texts_dir = os.path.join(target_dir, 'texts')
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(texts_dir, exist_ok=True)

    for item in items:
        image_url = item.get('image_url')
        text = item.get('text')
        if not image_url or not text:
            continue

        # 从 image_url 获取图片的相对路径
        image_relative_path = image_url.replace("/uploads/", "")
        image_path = os.path.join(UPLOAD_FOLDER, image_relative_path)

        if os.path.exists(image_path):
            # 复制图片到 images_dir
            shutil.copy(image_path, images_dir)
        else:
            logging.warning(f"图片文件不存在: {image_path}")

        # 保存文案到 texts_dir
        image_filename = os.path.basename(image_path)
        text_filename = os.path.splitext(image_filename)[0] + '.txt'
        text_path = os.path.join(texts_dir, text_filename)
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(text)

    return target_dir