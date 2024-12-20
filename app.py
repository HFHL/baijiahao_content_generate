# app.py

from flask import Flask, render_template, request, jsonify, send_from_directory, Response
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import json
import logging
from config import UPLOAD_FOLDER, SECRET_KEY, SAVED_FOLDER
from utils import (
    allowed_file, extract_all_zips, build_directory_tree, build_jstree_format,
    sanitize_path, get_image_paths, build_prompt, call_gpt_api, calculate_cost, save_generated_text,
    load_prompts, save_all_items
)
from dotenv import load_dotenv

load_dotenv()  # 加载 .env 文件中的环境变量

app = Flask(__name__)
app.secret_key = SECRET_KEY

# 配置日志
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    if file and allowed_file(file.filename):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        target_dir = os.path.join(UPLOAD_FOLDER, timestamp)
        os.makedirs(target_dir, exist_ok=True)
        filename = secure_filename(file.filename)
        file_path = os.path.join(target_dir, filename)
        file.save(file_path)
        # 解压
        extract_all_zips(target_dir)
        # 构建目录树
        tree = build_directory_tree(target_dir)
        logging.debug(f"目录树: {json.dumps(tree, ensure_ascii=False, indent=2)}")
        # 将目录树转换为jsTree格式
        js_tree = build_jstree_format(tree)
        logging.debug(f"jsTree格式: {json.dumps(js_tree, ensure_ascii=False, indent=2)}")
        return jsonify(js_tree)
    else:
        return "File type not allowed", 400

@app.route('/prompts', methods=['GET'])
def get_prompts():
    """
    返回所有可用的 Prompt 模板。
    """
    try:
        prompts = load_prompts()
        prompt_list = []
        for key, value in prompts.items():
            prompt_list.append({
                "key": key,
                "name": value.get("name", key)
            })
        logging.debug(f"返回的 prompt_list: {prompt_list}")
        return jsonify(prompt_list)
    except Exception as e:
        logging.error(f"加载 prompts 失败: {e}")
        return jsonify({"error": "无法加载提示模板"}), 500

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    if not data or 'paths' not in data or 'prompt' not in data:
        return jsonify({"error": "无效的请求数据"}), 400

    selected_paths = data['paths']
    selected_prompt = data['prompt']
    if not isinstance(selected_paths, list):
        return jsonify({"error": "路径应为列表"}), 400

    # 收集所有图片路径
    all_image_paths = []
    for path in selected_paths:
        sanitized_path = sanitize_path(path)
        full_path = os.path.join(UPLOAD_FOLDER, sanitized_path)
        if os.path.exists(full_path):
            image_paths = get_image_paths(full_path)
            all_image_paths.extend(image_paths)

    if not all_image_paths:
        return jsonify({"error": "未找到任何图片文件"}), 400

    # 定义生成器函数，用于流式传输结果
    def generate_stream_response(all_image_paths, selected_prompt):
        total_prompt_tokens = 0
        total_completion_tokens = 0
        items = []  # 用于保存所有生成的项

        for image_path in all_image_paths:
            # 构建提示
            template_key = selected_prompt  # 使用用户选择的模板
            prompt = build_prompt(template_key, image_path, use_url=False)  # 不使用外部存储

            # 调用GPT API
            generated_text, usage = call_gpt_api(prompt)

            # 计算费用
            if usage:
                prompt_tokens = usage.prompt_tokens
                completion_tokens = usage.completion_tokens
                cost_usd, cost_cny = calculate_cost(prompt_tokens, completion_tokens)
                total_prompt_tokens += prompt_tokens
                total_completion_tokens += completion_tokens
            else:
                prompt_tokens = completion_tokens = 0
                cost_usd = cost_cny = 0.0

            # 保存生成的文案
            save_generated_text(image_path, generated_text)

            # 获取图片的相对路径以构建URL
            image_relative_path = os.path.relpath(image_path, UPLOAD_FOLDER).replace(os.path.sep, '/')
            image_url = f"/uploads/{image_relative_path}"

            # 准备要发送的数据
            data_item = {
                "image_url": image_url,
                "text": generated_text,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "cost_usd": f"${cost_usd:.6f}",
                "cost_cny": f"￥{cost_cny:.6f}"
            }

            items.append(data_item)  # 添加到项列表

            # 使用 Server-Sent Events (SSE) 格式发送数据
            yield f"data: {json.dumps(data_item)}\n\n"

        # 发送总费用
        total_cost_usd, total_cost_cny = calculate_cost(total_prompt_tokens, total_completion_tokens)
        total_data = {
            "total_cost_usd": f"${total_cost_usd:.6f}",
            "total_cost_cny": f"￥{total_cost_cny:.6f}"
        }
        yield f"data: {json.dumps({'total_cost': total_data})}\n\n"

    # 返回流式响应
    return Response(generate_stream_response(all_image_paths, selected_prompt), mimetype='text/event-stream')

@app.route('/save', methods=['POST'])
def save_all():
    """
    保存所有生成的文案和对应的图片到指定的保存目录。
    """
    data = request.get_json()
    if not data or 'items' not in data:
        return jsonify({"error": "无效的请求数据"}), 400

    items = data['items']
    if not isinstance(items, list):
        return jsonify({"error": "items 应该是列表"}), 400

    try:
        saved_dir = save_all_items(SAVED_FOLDER, items)
        logging.debug(f"保存的目录: {saved_dir}")
        return jsonify({"message": "保存成功", "saved_dir": saved_dir}), 200
    except Exception as e:
        logging.error(f"保存失败: {e}")
        return jsonify({"error": "保存失败，请稍后再试。"}), 500

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# 错误处理（可选）
@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "上传的文件过大。最大允许大小为50MB。"}), 413

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "资源未找到。"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "服务器内部错误。请稍后再试。"}), 500

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(SAVED_FOLDER, exist_ok=True)  # 创建保存目录
    app.run(debug=True, threaded=True)