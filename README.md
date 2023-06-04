# Winter Optimization

First, you need to setup your environment. To do so, run the following command at the project's root: `pip install -r requirements.txt`.

Next you are given a script to execute the differents parts of our project.

* `./exec.sh -drone` will only run the computation of the drone price and path length.
* `./exec.sh -snow` will only run the computation of the snowplow part.
* `./exec.sh -a` will run both parts.

All the results will be stored in the file `res.txt`.
