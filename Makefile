.PHONY: lint-post test-xhs test-x test-social test-acceptance

# 用法: make lint-post POST=memory/<loop>/outputs/<post>
lint-post:
	@test -n "$(POST)" || (echo "usage: make lint-post POST=memory/<loop>/outputs/<post>"; exit 2)
	@python3 executors/xhs-render-cards/scripts/check-banned-phrases.py "$(POST)"
	@python3 executors/xhs-render-cards/scripts/check-compliance.py "$(POST)"

test-xhs:
	@python3 collectors/xiaohongshu-mcp/scripts/test_collect_xiaohongshu.py
	@python3 collectors/xiaohongshu-mcp/scripts/test_run_xiaohongshu.py
	@python3 collectors/xiaohongshu-mcp/scripts/test_auto_select_visual_reference.py
	@python3 collectors/xiaohongshu-mcp/scripts/test_validate_visual_reference_selection.py
	@python3 collectors/xiaohongshu-mcp/scripts/test_minimal_continuous_flow.py
	@python3 models/onboard-growth-lab/scripts/test_check_configuration.py
	@python3 executors/xhs-render-cards/scripts/test_validate_social_card_pack.py
	@node --check executors/generate-image/generate-image.mjs

test-x:
	@python3 collectors/x-browser/scripts/test_collect_x.py
	@python3 models/onboard-growth-lab/scripts/test_check_configuration.py

test-social:
	@python3 models/run-social-content-loop/scripts/test_validate_orchestration.py
	@python3 collectors/tests/test_official_social_api.py
	@python3 collectors/tests/test_social_browser_collectors.py
	@python3 executors/x-draft-stager/scripts/test_stage_x_draft.py

test-acceptance:
	@python3 scripts/acceptance/run_acceptance.py --tier offline
