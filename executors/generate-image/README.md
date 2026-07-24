# Generate Image Executor / 生图执行器

零依赖 Node.js Client，支持文生图和参考图编辑。默认使用 `gemini-3.1-flash-image-2k`，也可以选择 `gpt-image-2`。

## Gemini

```bash
export GEMINI_API_KEY='...'
# 可选；默认使用 Google 官方 API
export GOOGLE_GEMINI_BASE_URL='https://generativelanguage.googleapis.com'

node executors/generate-image/generate-image.mjs \
  --out public/seo/example.png \
  --prompt-file seo-work/image-prompt.txt
```

## OpenAI

```bash
export OPENAI_API_KEY='...'
# 可选；默认使用 OpenAI 官方 API
export OPENAI_BASE_URL='https://api.openai.com'

node executors/generate-image/generate-image.mjs \
  --model gpt-image-2 \
  --out public/seo/example.png \
  "A clear product illustration"
```

## Reference image editing / 参考图编辑

```bash
node executors/generate-image/generate-image.mjs \
  --model gpt-image-2 \
  --ref existing.png \
  --out edited.png \
  --prompt-file edit-prompt.txt
```

所有凭据只从进程环境变量读取。Executor 不读取 `~/.gemini/.env`、项目 `.env` 或其他隐式配置文件，不复用另一家服务的 API key，也不输出请求头、带签名的图片 URL 或完整 API 响应。

生成完成后，Agent 必须使用 Runtime 的图片查看能力检查图片内容、文字、裁切和视觉瑕疵。页面图片还需要配置描述性 alt、明确尺寸和适合页面加载的格式。
