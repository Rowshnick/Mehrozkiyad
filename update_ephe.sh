#!/bin/bash

set -e

echo "🔄 Updating ephe folder from SwissEph..."

# 1) پاک کردن نسخه قبلی
rm -rf ephe
echo "✅ Old ephe folder removed."

# 2) دانلود فولدر ephe از GitHub (به صورت ZIP)
curl -L https://github.com/aloistr/swisseph/archive/refs/heads/master.zip -o swisseph.zip
echo "✅ Downloaded SwissEph ZIP."

# 3) استخراج فایل ZIP
unzip -q swisseph.zip
echo "✅ Extracted ZIP."

# 4) کپی فولدر ephe به ریپوی تو
cp -r swisseph-master/ephe ./ephe
echo "✅ Copied ephe folder into your repo."

# 5) پاک‌سازی فایل‌های اضافی
rm -rf swisseph.zip swisseph-master
echo "✅ Cleanup done."

# 6) Commit و Push
git add ephe
git commit -m "Update ephe folder from SwissEph"
git push

echo "✅ All done! ephe folder updated and pushed to GitHub."
