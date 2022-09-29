cd %AppData%\Kodi\addons
git pull

git python update_repo.py
git python update-directory-structure.py

git add .
git commit -a -m "update repo"
git push

pause
 python 