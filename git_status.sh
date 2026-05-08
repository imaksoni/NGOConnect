git status -s > status.txt
cat status.txt | grep "flutter_app/lib/" || echo "No lib files in status"
