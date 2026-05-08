git diff --cached --name-only > files_to_commit.txt
cat files_to_commit.txt | grep "flutter_app/lib/" || echo "no lib files in staging"
