if [ $# -eq 0 ]; then
  echo "Usage : ./exec -a : execute all"
  echo "      : ./exec -drone : execute drone script"
  echo "      : ./exec -snow : execute deneigeuse script"
  exit 1
fi 

if [ "$1" = "-a" ]; then
  python3 ./compute_drone/compute_drone_path_and_price.py > res.txt
  printf "\n -------------------- \n\n" >> res.txt
  python3 ./compute_deneigeuse/compute_deneigeuse.py >> res.txt
  exit 0
fi

if [ "$1" = "-drone" ]; then
  python3 ./compute_drone/compute_drone_path_and_price.py > res.txt
  exit 0
fi

if [ "$1" = "-snow" ]; then
  python3 ./compute_deneigeuse/compute_deneigeuse.py > res.txt
  exit 0
fi

echo "invalid arg: $1"
exit 1
