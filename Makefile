PY ?= python3
export SOURCE_DATE_EPOCH := 1761955200
check: l0
l0:
	@for d in repro/*/; do echo "== $$d"; (cd $$d && $(PY) l0_check.py | tail -1 | grep -q "L0 PASS") || { echo "L0 failed in $$d"; exit 1; }; done
.PHONY: check l0
