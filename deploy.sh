#!/usr/bin/env bash
# Publish ai4s.runixcloud.io to Cloudflare Pages (direct upload).
#
#   ./deploy.sh                 # build, verify, upload, then check the live site
#   ./deploy.sh --dry-run       # everything except the upload
#
# The API token is read from the login keychain, the same place runix-site
# keeps it. It is never printed and never written to disk.
set -euo pipefail

PROJECT="ai4s-course"
PROD_BRANCH="main"
DOMAIN="https://ai4s.runixcloud.io"
SRC="$(cd "$(dirname "$0")" && pwd)"
DRY=0
[ "${1:-}" = "--dry-run" ] && DRY=1

cd "$SRC"

echo "==> Rebuild and lint"
# build.py fails on over-long titles, badly sized meta descriptions, duplicate
# metadata and dead internal links. None of those are visible in a browser,
# which is exactly why they belong in front of a deploy rather than behind it.
python3 build.py

echo "==> dist/ matches the sources"
python3 build.py --check

echo "==> Client JavaScript parses"
node --check assets/site.js
node --check assets/quiz.js

echo "==> Offline labs still run"
# Prefer a project venv; fall back to whatever python3 is on PATH.
LAB_PY="python3"
[ -x "$SRC/.venv/bin/python" ] && LAB_PY="$SRC/.venv/bin/python"
if "$LAB_PY" -c "import pandas, gemmi" 2>/dev/null; then
  "$LAB_PY" labs/lab1_read_one_record.py > /dev/null
  "$LAB_PY" labs/lab2_data_checkup.py    > /dev/null
  "$LAB_PY" labs/lab5_compute_epitope.py > /dev/null
  echo "    ok ($LAB_PY)"
else
  # Say so out loud. A check that quietly turns into a no-op is worse than no
  # check at all — CI runs these on every push, so the deploy is not blocked.
  echo "    SKIPPED: pandas/gemmi not available to $LAB_PY"
  echo "             (CI runs these on every push; install with"
  echo "              pip install -r labs/requirements.txt to check locally)"
fi

if [ "$DRY" = "1" ]; then
  echo
  echo "Dry run complete. $(find dist -type f | wc -l | tr -d ' ') files, $(du -sh dist | cut -f1) in dist/."
  exit 0
fi

TOKEN="$(security find-generic-password -a "$USER" -s runix-cf-token -w 2>/dev/null || true)"
if [ -z "$TOKEN" ]; then
  echo "No Cloudflare token in the keychain (service: runix-cf-token)." >&2
  echo "Add one with Pages:Edit scope, or export CLOUDFLARE_API_TOKEN yourself." >&2
  exit 1
fi

echo "==> Upload to Cloudflare Pages project '$PROJECT'"
CLOUDFLARE_API_TOKEN="$TOKEN" npx --yes wrangler@latest pages deploy dist \
  --project-name "$PROJECT" --branch "$PROD_BRANCH" --commit-dirty=true

# Cloudflare's edge needs a moment to pick up a fresh deployment, and the
# verification below is the only thing that distinguishes "uploaded" from
# "actually live" — the distinction that matters.
echo "==> Verify the live site"
sleep 6
fail=0
for path in / /course/ /course/formats-and-ids/ /course/falsification/ \
            /labs/ /quiz/ /glossary/ /resources/ /en/ \
            /sitemap.xml /robots.txt /assets/og/default.png; do
  code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 20 "$DOMAIN$path" || echo 000)"
  printf '    %-34s %s\n' "$path" "$code"
  [ "$code" = "200" ] || fail=1
done

if [ "$fail" != "0" ]; then
  echo
  echo "Some pages did not return 200. If the custom domain is not attached yet," >&2
  echo "check the *.pages.dev URL printed above instead." >&2
  exit 1
fi

echo
echo "Live: $DOMAIN"
echo "Next: submit $DOMAIN/sitemap.xml in Google Search Console and Bing Webmaster Tools."
