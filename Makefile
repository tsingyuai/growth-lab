.PHONY: lint-post test-xhs wechat-post-required wechat-lint wechat-preview wechat-render wechat-draft wechat-publish wechat-status \
	wechat-remote-draft wechat-remote-publish wechat-remote-status wechat-publisher-build

WECHAT_CLI := python3 executors/wechat-mp-publish/scripts/cli.py
WECHAT_REMOTE := python3 executors/wechat-mp-publish/scripts/remote_client.py

# 用法: make lint-post POST=memory/<loop>/outputs/<post>
lint-post:
	@test -n "$(POST)" || (echo "usage: make lint-post POST=memory/<loop>/outputs/<post>"; exit 2)
	@python3 executors/xhs-render-cards/scripts/check-banned-phrases.py "$(POST)"
	@python3 executors/xhs-render-cards/scripts/check-compliance.py "$(POST)"

test-xhs:
	@python3 collectors/xiaohongshu-mcp/scripts/test_collect_xiaohongshu.py
	@python3 collectors/xiaohongshu-mcp/scripts/test_validate_visual_reference_selection.py
	@python3 collectors/xiaohongshu-mcp/scripts/test_minimal_continuous_flow.py
	@python3 models/onboard-growth-lab/scripts/test_check_configuration.py
	@python3 executors/xhs-render-cards/scripts/test_validate_social_card_pack.py
	@node --check executors/generate-image/generate-image.mjs

# 微信公众号。用法: make wechat-<target> POST=memory/run-wechat-article-loop/outputs/<slug>
wechat-post-required:
	@test -n "$(POST)" || (echo "usage: make $(MAKECMDGOALS) POST=memory/run-wechat-article-loop/outputs/<slug>"; exit 2)

wechat-lint: wechat-post-required
	@python3 executors/wechat-article-compose/scripts/check-wechat-compliance.py "$(POST)"

wechat-preview: wechat-post-required
	@$(WECHAT_CLI) preview "$(POST)" --open

wechat-render: wechat-post-required
	@$(WECHAT_CLI) render "$(POST)" --payload

wechat-draft: wechat-lint
	@$(WECHAT_CLI) draft "$(POST)"

wechat-publish: wechat-lint
	@$(WECHAT_CLI) publish "$(POST)" --confirm-publish

wechat-status: wechat-post-required
	@$(WECHAT_CLI) status "$(POST)"

wechat-remote-draft: wechat-lint
	@$(WECHAT_REMOTE) draft "$(POST)"

wechat-remote-publish: wechat-lint
	@$(WECHAT_REMOTE) publish "$(POST)" --upload --confirm-publish

wechat-remote-status: wechat-post-required
	@$(WECHAT_REMOTE) status "$(POST)"

wechat-publisher-build:
	@docker build -f executors/wechat-mp-publish/deploy/Dockerfile -t wechat-publisher:latest .
