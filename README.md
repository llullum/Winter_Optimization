# Winter Optimization
## Installation and execution
First, you need to setup your environment. To do so, run the following command at the project's root: `pip install -r requirements.txt`.

Next you are given a script to execute the differents parts of our project.

* `./exec.sh -drone` will only run the computation of the drone price and path length.
* `./exec.sh -snow` will only run the computation of the snowplow part.
* `./exec.sh -a` will run both parts.

All the results will be stored in the file `res.txt`.

## Structure

* `compute_deneigeuse/`
  * `compute_deneigeuse.py` (compute the price of the snowplows for Rivière-des-Prairies–Pointe-aux-Trembles, Outremont, Saint-Léonard, Le Plateau-Mont-Royal and Verdun)
* `compute_drone/`
  * `compute_drone_path_and_price.py` (compute the price of the drones for Montréal)
* `AUTHORS` (names of the group's members)
* `compute_path.py` (utily functions to manipulate graphs)
* `exec.sh` (wrapper to easily execute the project)
* `requirements.txt` (python modules to run the project)
