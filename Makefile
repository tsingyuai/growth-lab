.PHONY: lint-post render

# 用法: make lint-post POST=memory/<loop>/outputs/<post>
lint-post:
	@test -n "$(POST)" || (echo "usage: make lint-post POST=memory/<loop>/outputs/<post>"; exit 2)
	@python3 executors/xhs-render-cards/scripts/check-banned-phrases.py "$(POST)"
	@python3 executors/xhs-render-cards/scripts/check-compliance.py "$(POST)"

# 用法: make render POST=memory/<loop>/outputs/<post>
render:
	@test -n "$(POST)" || (echo "usage: make render POST=memory/<loop>/outputs/<post>"; exit 2)
	@uv run --with playwright --with jinja2 python executors/xhs-render-cards/scripts/render.py \
		--input "$(POST)/cards.json" --output "$(POST)/img"
