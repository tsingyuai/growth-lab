.PHONY: lint-post

# 用法: make lint-post POST=memory/<loop>/outputs/<post>
lint-post:
	@test -n "$(POST)" || (echo "usage: make lint-post POST=memory/<loop>/outputs/<post>"; exit 2)
	@python3 executors/xhs-render-cards/scripts/check-banned-phrases.py "$(POST)"
	@python3 executors/xhs-render-cards/scripts/check-compliance.py "$(POST)"
