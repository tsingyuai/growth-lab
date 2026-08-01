.PHONY: lint-post test-xhs

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
