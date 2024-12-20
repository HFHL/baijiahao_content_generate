// static/js/scripts.js

$(document).ready(function() {
    // 动态加载 Prompt 模板
    $.ajax({
        url: '/prompts',
        type: 'GET',
        success: function(response) {
            console.log("加载的 Prompt 模板:", response);
            var promptSelect = $('#prompt-select');
            response.forEach(function(prompt) {
                var option = `<option value="${prompt.key}">${prompt.name}</option>`;
                promptSelect.append(option);
            });
        },
        error: function(xhr, status, error) {
            console.error('加载文案模板失败:', xhr.responseText);
            alert('加载文案模板失败，请查看控制台获取更多信息。');
        }
    });

    // 监听文件上传表单提交
    $('#upload-form').on('submit', function(e) {
        e.preventDefault(); // 阻止默认提交

        var formData = new FormData(this);

        $.ajax({
            url: $(this).attr('action'),
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            beforeSend: function() {
                // 上传过程中可以显示加载指示器（可选）
            },
            success: function(response) {
                // 清空现有的树
                $('#directory-tree').jstree('destroy');
                // 初始化jsTree
                $('#directory-tree').jstree({
                    'core': {
                        'data': response,
                        'themes': {
                            'responsive': false
                        }
                    },
                    'plugins': ["search", "checkbox"]
                });

                // 监听节点选中事件
                $('#directory-tree').on('changed.jstree', function(e, data) {
                    var selectedNodes = data.selected;
                    if(selectedNodes.length > 0 && $('#prompt-select').val()){
                        $('#generate-button').show();
                    } else {
                        $('#generate-button').hide();
                    }

                    // 也决定是否显示“保存所有”按钮
                    $('#save-all-button').hide(); // 清空生成结果时隐藏保存按钮
                });

                // 监听 Prompt 选择变化事件
                $('#prompt-select').on('change', function() {
                    var selectedPrompt = $(this).val();
                    var selectedNodes = $('#directory-tree').jstree('get_selected');
                    if(selectedNodes.length > 0 && selectedPrompt){
                        $('#generate-button').show();
                    } else {
                        $('#generate-button').hide();
                    }

                    // 也决定是否显示“保存所有”按钮
                    $('#save-all-button').hide(); // 清空生成结果时隐藏保存按钮
                });
            },
            error: function(xhr, status, error) {
                console.error('上传失败:', xhr.responseText);
                alert('上传失败: ' + xhr.responseText);
            }
        });
    });

    // 存储所有生成的项
    var allGeneratedItems = [];

    // 监听“生成”按钮点击事件
    $('#generate-button').on('click', function() {
        // 获取选中的节点
        var selectedNodes = $('#directory-tree').jstree('get_selected', true);
        var selectedPaths = [];

        selectedNodes.forEach(function(node) {
            selectedPaths.push(node.id);
        });

        if(selectedPaths.length === 0){
            alert("请先选择要生成的目录或图片。");
            return;
        }

        // 获取选中的 Prompt 模板
        var selectedPrompt = $('#prompt-select').val();
        if(!selectedPrompt){
            alert("请先选择一个文案模板。");
            return;
        }

        // 清空之前的结果并显示加载指示器
        $('#generation-results').empty();
        $('#generation-results').html('<p class="text-center">正在生成，请稍候...</p>');
        $('#save-all-button').hide(); // 生成前隐藏保存按钮
        allGeneratedItems = []; // 重置生成项列表

        // 使用 Fetch API 发送 POST 请求，并处理流式响应
        fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ paths: selectedPaths, prompt: selectedPrompt })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('网络响应不是OK');
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            function read() {
                reader.read().then(({ done, value }) => {
                    if (done) {
                        // 生成结束，显示“保存所有”按钮
                        if (allGeneratedItems.length > 0) {
                            $('#save-all-button').show();
                        }
                        return;
                    }
                    buffer += decoder.decode(value, { stream: true });
                    let boundary = '\n\n';
                    let parts = buffer.split(boundary);
                    buffer = parts.pop(); // 剩余部分
                    parts.forEach(part => {
                        if (part.startsWith('data: ')) {
                            let jsonStr = part.slice(6).trim();
                            if (jsonStr) {
                                try {
                                    let dataItem = JSON.parse(jsonStr);
                                    if (dataItem.image_url && dataItem.text) {
                                        allGeneratedItems.push(dataItem); // 添加到项列表

                                        // 创建并渲染卡片
                                        var card = `
                                            <div class="col">
                                                <div class="card h-100">
                                                    <img src="${dataItem.image_url}" class="card-img-top" alt="图片">
                                                    <div class="card-body d-flex flex-column">
                                                        <p class="card-text">${dataItem.text}</p>
                                                        <div class="mt-auto">
                                                            <p class="card-text"><small class="text-muted">Token使用: 提示 ${dataItem.prompt_tokens}, 补全 ${dataItem.completion_tokens}</small></p>
                                                            <p class="card-text"><small class="text-muted">费用: ${dataItem.cost_usd} / ${dataItem.cost_cny}</small></p>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        `;
                                        $('#generation-results').append(card);
                                    }
                                    if (dataItem.total_cost) {
                                        var totalCost = `
                                            <div class="col-12">
                                                <div class="alert alert-info text-center" role="alert">
                                                    <strong>总费用:</strong> ${dataItem.total_cost.total_cost_usd} / ${dataItem.total_cost.total_cost_cny}
                                                </div>
                                            </div>
                                        `;
                                        $('#generation-results').append(totalCost);
                                    }
                                } catch (e) {
                                    console.error('JSON解析错误:', e);
                                }
                            }
                        }
                    });
                    read(); // 继续读取
                }).catch(error => {
                    console.error('读取错误:', error);
                    alert('生成失败: ' + error.message);
                    $('#generation-results').empty();
                });
            }

            read(); // 开始读取
        })
        .catch(error => {
            console.error('生成失败:', error);
            alert('生成失败: ' + error.message);
            $('#generation-results').empty();
        });
    });

    // 监听“保存所有”按钮点击事件
    $('#save-all-button').on('click', function() {
        if (allGeneratedItems.length === 0) {
            alert("没有可保存的内容。");
            return;
        }

        // 发送保存请求到后端
        fetch('/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ items: allGeneratedItems })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert("保存成功！目录: " + data.saved_dir);
                $('#save-all-button').hide(); // 保存后隐藏按钮
            } else if (data.error) {
                alert("保存失败: " + data.error);
            }
        })
        .catch(error => {
            console.error('保存失败:', error);
            alert('保存失败: ' + error.message);
        });
    });
});