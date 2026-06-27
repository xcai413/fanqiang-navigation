#!/bin/bash
# Push fanqiang-navigation via gh API (since git://github.com:443 is blocked)
set -e

OWNER="xcai413"
REPO="fanqiang-navigation"
BASE="/d/ale/yoximen/fanqiang-navigation"

echo "=== Step 1: Collecting files ==="
declare -a PATHS
declare -a CONTENTS
cd "$BASE"
while IFS= read -r f; do
    rel="${f#./}"
    # Skip .git
    [[ "$rel" == .git/* || "$rel" == .git ]] && continue
    echo "  $rel"
    PATHS+=("$rel")
    CONTENTS+=("$(base64 -w0 "$rel")")
done < <(find . -type f | sort)

echo ""
echo "Total: ${#PATHS[@]} files"

echo "=== Step 2: Creating blobs ==="
declare -a BLOB_SHAS
for i in "${!PATHS[@]}"; do
    echo "  blob ${PATHS[$i]}"
    result=$(gh api "repos/$OWNER/$REPO/git/blobs" \
      --method POST \
      --field content="${CONTENTS[$i]}" \
      --field encoding="base64" \
      --jq '.sha' 2>/dev/null)
    BLOB_SHAS+=("$result")
done

echo "=== Step 3: Creating tree ==="
TREE_ITEMS="["
for i in "${!PATHS[@]}"; do
    [ "$i" -gt 0 ] && TREE_ITEMS+=","
    TREE_ITEMS+="{\"path\":\"${PATHS[$i]}\",\"mode\":\"100644\",\"type\":\"blob\",\"sha\":\"${BLOB_SHAS[$i]}\"}"
done
TREE_ITEMS+="]"

tree_sha=$(gh api "repos/$OWNER/$REPO/git/trees" \
  --method POST \
  --field tree="$TREE_ITEMS" \
  --jq '.sha')
echo "Tree: $tree_sha"

echo "=== Step 4: Creating commit ==="
commit_sha=$(gh api "repos/$OWNER/$REPO/git/commits" \
  --method POST \
  --field message="🎉 初始化项目结构

README 中英双语 · 免费节点 · 机场推荐 · 教程 · GitHub Actions" \
  --field tree="$tree_sha" \
  --field 'author={"name":"xcai413","email":"xcai413@users.noreply.github.com"}' \
  --jq '.sha')
echo "Commit: $commit_sha"

echo "=== Step 5: Updating branch ==="
gh api "repos/$OWNER/$REPO/git/refs" \
  --method POST \
  --field ref="refs/heads/master" \
  --field sha="$commit_sha" \
  --jq '.ref'
echo ""
echo "✅ DONE! https://github.com/$OWNER/$REPO"
