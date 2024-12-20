Baijiahao 文件管理系统

目录
	•	项目简介
	•	功能特性
	•	技术栈
	•	项目结构
	•	安装与配置
	•	使用指南
	•	模块设计
	•	流程设计
	•	贡献指南
	•	许可证

项目简介

Baijiahao 文件管理系统是一个基于 Flask 的 Web 应用，旨在帮助用户上传包含图片的压缩文件，生成与图片相关的文案，并将生成的文案及对应的图片保存到指定目录中。该系统集成了 OpenAI 的 GPT 模型，用于自动生成高质量的文案，提升内容创作效率。

功能特性
	•	文件上传与解压：支持上传多层级目录结构的 .zip 文件，自动解压并构建目录树。
	•	目录树展示：使用 jsTree 展示上传文件的目录结构，支持搜索与多选。
	•	文案模板选择：提供多种文案生成模板，用户可根据需求选择合适的模板。
	•	文案生成：基于选定的图片和模板，通过 OpenAI GPT API 生成相关文案。
	•	实时展示：生成的文案和对应图片实时显示在界面上。
	•	保存功能：一键保存所有生成的文案及图片到专门的目录，便于管理与后续使用。
	•	现代化界面：采用简约且具设计感的界面，提升用户体验。

技术栈
	•	后端：
	•	Python 3.x
	•	Flask
	•	OpenAI API
	•	Werkzeug
	•	Python-dotenv
	•	前端：
	•	HTML5
	•	CSS3 (Bootstrap 5)
	•	JavaScript (jQuery)
	•	jsTree
	•	工具：
	•	Git
	•	VS Code (或其他 IDE)
	•	GitHub (代码托管)

项目结构

baijiahao/
├── app.py
├── config.py
├── utils.py
├── prompts/
│   └── prompts.json
├── uploads/
│   └── [timestamp]/
│       ├── [uploaded_files]
│       └── generated_texts/
│           └── [text_files]
├── saved_items/
│   └── save_[timestamp]/
│       ├── images/
│       └── texts/
├── templates/
│   └── index.html
├── static/
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── scripts.js
├── .env
├── .gitignore
└── README.md

目录说明
	•	app.py：Flask 应用的主文件，定义了所有路由和核心逻辑。
	•	config.py：配置文件，包含应用的配置信息，如上传目录、保存目录等。
	•	utils.py：工具模块，包含辅助函数，如文件处理、API 调用等。
	•	prompts/prompts.json：存放文案生成模板的 JSON 文件。
	•	uploads/：存放用户上传的文件，按时间戳分目录管理。
	•	saved_items/：保存用户通过“保存所有”功能保存的文案及图片，按时间戳分目录管理。
	•	templates/index.html：前端主页面模板。
	•	static/css/styles.css：自定义的 CSS 样式表。
	•	static/js/scripts.js：前端的自定义 JavaScript 脚本。
	•	.env：环境变量文件，存放敏感信息和配置信息（不应上传到版本控制）。
	•	.gitignore：Git 忽略文件配置。
	•	README.md：项目说明文件。

安装与配置

前提条件
	•	Python 3.x 已安装
	•	Git 已安装
	•	OpenAI API 密钥

克隆项目

git clone https://github.com/yourusername/baijiahao.git
cd baijiahao

创建虚拟环境

建议使用虚拟环境管理项目依赖：

python -m venv venv
source venv/bin/activate  # 对于 Windows: venv\Scripts\activate

安装依赖

pip install -r requirements.txt

注意：确保 requirements.txt 文件包含所有必要的依赖包，例如：

Flask
Werkzeug
python-dotenv
openai
Pillow

配置环境变量

在项目根目录创建一个 .env 文件，添加以下内容：

SECRET_KEY=your_secret_key_here
UPLOAD_FOLDER=/absolute/path/to/uploads
PROMPT_FILE=/absolute/path/to/prompts/prompts.json
SAVED_FOLDER=/absolute/path/to/saved_items
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL_NAME=gpt-4

注意：
	•	替换 /absolute/path/to/... 为实际的绝对路径。
	•	确保 .env 文件不会被上传到版本控制系统。

初始化目录

确保上传和保存目录存在：

mkdir -p uploads
mkdir -p saved_items
mkdir -p prompts

将 prompts.json 放置在 prompts/ 目录中。

运行应用

python app.py

应用将在 http://localhost:5000/ 运行。

使用指南
	1.	访问应用：
打开浏览器，访问 http://localhost:5000/。
	2.	上传文件：
	•	点击“上传文件”区域，选择一个包含多层级目录和图片的 .zip 文件。
	•	上传完成后，目录树将自动展示上传的文件结构。
	3.	选择文案模板：
	•	在“选择文案模板”区域，从下拉菜单中选择一个合适的文案模板（如“推荐类”或“广告类”）。
	•	选择模板后，确保已选中至少一个目录或图片，生成按钮将可用。
	4.	生成文案：
	•	选中目录或图片，点击“生成文案”按钮。
	•	系统将通过 OpenAI GPT API 生成相关文案，并实时展示在“生成结果”区域。
	5.	保存生成内容：
	•	生成完成后，点击固定在页面右下角的“保存所有”按钮，将所有生成的文案及对应图片保存到 saved_items/ 目录中。

模块设计

1. app.py
	•	职责：
	•	定义 Flask 应用及其路由。
	•	处理文件上传、文案生成和保存请求。
	•	管理应用的整体流程和逻辑。
	•	主要路由：
	•	/：主页面，渲染 index.html。
	•	/upload：处理文件上传和解压。
	•	/prompts：提供文案模板列表。
	•	/generate：生成文案，使用 SSE 流式传输结果。
	•	/save：保存所有生成的文案和图片。
	•	/uploads/<path:filename>：提供上传文件的访问路径。

2. config.py
	•	职责：
	•	存放应用的配置信息和路径设置。
	•	从环境变量加载敏感信息。
	•	关键配置项：
	•	SECRET_KEY：Flask 应用的密钥。
	•	UPLOAD_FOLDER：上传文件的存储目录。
	•	PROMPT_FILE：文案模板文件的路径。
	•	SAVED_FOLDER：保存生成内容的目录。
	•	OPENAI_API_KEY：OpenAI API 密钥。
	•	OPENAI_BASE_URL 和 OPENAI_MODEL_NAME：OpenAI API 的基础 URL 和模型名称。

3. utils.py
	•	职责：
	•	提供辅助函数，简化主应用逻辑。
	•	处理文件操作、API 调用和数据处理。
	•	主要功能：
	•	文件处理：
	•	allowed_file(filename)：检查上传文件类型。
	•	extract_all_zips(dir_path)：递归解压目录中的所有 .zip 文件。
	•	build_directory_tree(path)：构建目录树结构。
	•	build_jstree_format(tree, parent_id="#")：将目录树转换为 jsTree 格式。
	•	文案生成：
	•	load_prompts()：加载文案模板。
	•	build_prompt(template_key, image_path, use_url=False)：根据模板和图片构建生成提示。
	•	call_gpt_api(prompt)：调用 OpenAI GPT API 生成文案。
	•	save_generated_text(image_path, generated_text)：保存生成的文案到文本文件。
	•	calculate_cost(prompt_tokens, completion_tokens)：计算 API 调用费用。
	•	保存功能：
	•	save_all_items(saved_folder, items)：将所有生成的文案和图片保存到指定目录。

4. prompts/prompts.json
	•	职责：
	•	存储不同类型的文案生成模板。
	•	提供模板名称、指令、必要条件和辅助条件。
	•	示例结构：

{
    "recommend": {
        "name": "推荐类",
        "instructions": "结合图片中内容，写一篇20-450字以内小红书格式的动态内容，而且内容方面必须同时满足下列3点必要要求条件，同时要参考辅助要求的条件。",
        "necessary": [
            "方向定义：针对具体商品的展示、推荐、测评等，需要从个人使用体验出发，给用户准确的推荐理由。",
            "图文相符：文字内容需要和图片相对应，不要出现“小红书”、“动态内容”、“图片展示”“互动时间”、“真实分享”、“测评推荐”等字眼。",
            "文章风格要活泼，需要包含与用户互动的相关话术，主要以图片为主，文字为辅。"
        ],
        "auxiliary": [
            "真实分享：结合个人使用体验和客观商品参数，针对单品进行推荐或不推荐。",
            "测评推荐：结合个人使用体验和客观商品参数，同时推荐或不推荐多种商品。"
        ]
    },
    "advertisement": {
        "name": "广告类",
        "instructions": "结合图片中内容，撰写一篇20-450字以内的广告文案，必须满足以下3点必要要求，并参考辅助要求。",
        "necessary": [
            "突出产品特点：明确展示产品的独特卖点和优势。",
            "行动号召：引导用户进行购买或了解更多信息。",
            "简洁明了：文案需简洁有力，避免冗长。"
        ],
        "auxiliary": [
            "情感共鸣：通过情感化的语言与用户建立连接。",
            "视觉描述：详细描述图片中的元素，增强文案的吸引力。"
        ]
    }
    // 可以根据需要添加更多的 Prompt 模板
}



5. templates/index.html
	•	职责：
	•	定义应用的前端界面。
	•	使用 Bootstrap 和 jsTree 构建响应式、现代化的用户界面。
	•	关键组成部分：
	•	上传区域：文件上传表单，允许用户上传 .zip 文件。
	•	模板选择：下拉菜单，供用户选择文案生成模板。
	•	目录树：展示上传文件的目录结构，支持搜索与多选。
	•	生成结果：显示生成的文案及对应图片，使用卡片布局。
	•	保存按钮：固定在页面右下角的“保存所有”按钮，保存所有生成内容。

6. static/css/styles.css
	•	职责：
	•	自定义 CSS 样式，增强界面的美观与一致性。
	•	覆盖或扩展 Bootstrap 的默认样式。
	•	关键样式：
	•	卡片样式：添加阴影、悬停效果，提升视觉层次。
	•	按钮样式：设计圆形的“保存所有”按钮，固定在页面位置。
	•	响应式调整：确保在不同设备上界面元素合理排列。

7. static/js/scripts.js
	•	职责：
	•	实现前端的交互功能，如文件上传、文案生成、保存操作。
	•	处理与后端的 AJAX 请求和 SSE 流式响应。
	•	主要功能：
	•	加载文案模板：通过 AJAX 请求获取模板列表，填充下拉菜单。
	•	文件上传处理：上传 .zip 文件，初始化 jsTree 展示目录结构。
	•	文案生成：发送选定目录或图片和模板信息到后端，实时展示生成的文案和图片。
	•	保存功能：收集所有生成的内容，发送保存请求到后端，保存到指定目录。

流程设计

1. 用户上传文件
	•	用户在“上传文件”区域选择一个包含多层级目录和图片的 .zip 文件。
	•	前端通过 AJAX 请求将文件上传到后端的 /upload 路由。
	•	后端接收文件，解压到 UPLOAD_FOLDER 目录中，构建目录树结构，并返回给前端。
	•	前端使用 jsTree 展示上传后的目录结构。

2. 选择文案模板
	•	用户在“选择文案模板”下拉菜单中选择一个适合的模板（如“推荐类”或“广告类”）。
	•	前端记录用户的选择，并在选定目录或图片后，启用“生成文案”按钮。

3. 生成文案
	•	用户选择一个或多个目录或图片文件，点击“生成文案”按钮。
	•	前端发送 AJAX POST 请求到后端的 /generate 路由，包含选定的路径和模板信息。
	•	后端处理请求：
	•	根据选定路径收集所有图片文件路径。
	•	对每张图片，构建文案生成的提示信息。
	•	调用 OpenAI GPT API 生成文案。
	•	计算生成过程的费用。
	•	保存生成的文案到相应的文本文件。
	•	通过 Server-Sent Events (SSE) 将生成结果实时传回前端。
	•	前端接收 SSE 流式响应，实时在“生成结果”区域展示每张图片对应的文案和费用信息。
	•	生成完成后，显示“保存所有”按钮。

4. 保存生成内容
	•	用户点击“保存所有”按钮，前端收集所有生成的文案和图片信息。
	•	前端发送 AJAX POST 请求到后端的 /save 路由，包含所有生成的内容。
	•	后端处理请求：
	•	创建一个新的保存目录（按时间戳命名）以避免文件冲突。
	•	将所有生成的图片复制到 saved_items/save_[timestamp]/images/ 目录中。
	•	将对应的文案保存到 saved_items/save_[timestamp]/texts/ 目录中。
	•	后端返回保存成功的消息和保存目录路径。
	•	前端提示用户保存成功，并隐藏“保存所有”按钮。

贡献指南

欢迎为 Baijiahao 文件管理系统贡献代码！请按照以下步骤进行：
	1.	Fork 项目：点击右上角的 Fork 按钮，将项目仓库 Fork 到你的 GitHub 账户中。
	2.	克隆仓库：

git clone https://github.com/yourusername/baijiahao.git
cd baijiahao


	3.	创建分支：

git checkout -b feature/your-feature-name


	4.	提交更改：

git add .
git commit -m "描述你的更改"


	5.	推送到分支：

git push origin feature/your-feature-name


	6.	创建 Pull Request：在 GitHub 上创建一个新的 Pull Request，描述你的更改和改进。

许可证

本项目采用 MIT 许可证。详情请参阅 LICENSE 文件。

注意：本项目中涉及敏感信息（如 .env 文件中的 API 密钥），请确保这些信息不被上传到版本控制系统。使用 .gitignore 文件忽略相关文件和目录。

联系方式

如有任何问题或建议，请通过以下方式联系我：
	•	邮箱：your.email@example.com
	•	GitHub：https://github.com/yourusername

感谢您使用 Baijiahao 文件管理系统！希望它能帮助您高效管理文件并生成优质文案。